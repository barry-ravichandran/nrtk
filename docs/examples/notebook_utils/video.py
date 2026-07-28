"""Display and I/O helpers shared by the NRTK video-perturber example notebooks."""

from __future__ import annotations

import colorsys

import av
import matplotlib.pyplot as plt
import numpy as np
from av.video.reformatter import VideoReformatter
from IPython.display import HTML
from matplotlib import animation, font_manager
from PIL import Image, ImageDraw, ImageFont

import nrtk.experimental  # noqa: F401
from nrtk.interfaces import VideoFrame


def read_video(file_path: str, *, max_frames: int | None = None) -> list[VideoFrame]:
    """Read video frames into a list of VideoFrame objects."""
    reformatter = VideoReformatter()
    container = av.open(file_path, mode="r")
    frames: list[VideoFrame] = []
    for raw_frame in container.decode(video=0):
        image = reformatter.reformat(raw_frame, format="rgb24").to_ndarray()
        frames.append(VideoFrame(image=image, timestamp=raw_frame.time))
        if max_frames is not None and len(frames) >= max_frames:
            break
    container.close()
    return frames


def video_comparison(  # noqa: C901
    frame_sequences: list[list[np.ndarray]],
    *,
    titles: list[str],
    interval: int = 100,
    n_cols: int | None = None,
    figsize: tuple[float, float] | None = None,
) -> HTML:
    """Create a multi-panel video animation from frame sequences.

    Each entry in ``frame_sequences`` is a list of numpy images (all
    lists must be the same length). Panels are laid out on a grid;
    ``n_cols`` sets the number of columns (default: up to 3, then wrap
    onto additional rows). Returns an HTML5 ``<video>`` element that
    plays inline in Jupyter.
    """
    n = len(frame_sequences)
    if n_cols is None:
        n_cols = min(n, 3)
    n_cols = max(1, min(n_cols, n))
    nrows = (n + n_cols - 1) // n_cols  # ceil division
    if figsize is None:
        figsize = (5 * n_cols, 4 * nrows)
    fig, axes = plt.subplots(nrows=nrows, ncols=n_cols, figsize=figsize, squeeze=False)
    flat_axes = axes.ravel()  # row-major, always 1-D even for a single panel
    ims = []
    for idx, (title, seq) in enumerate(zip(titles, frame_sequences, strict=False)):
        ax = flat_axes[idx]
        ax.set_title(title)
        ax.axis("off")
        ims.append(ax.imshow(seq[0]))
    for ax in flat_axes[n:]:  # hide any empty cells in the last row
        ax.axis("off")
    plt.tight_layout()
    plt.close(fig)

    def animate(i: int) -> list:
        for im, seq in zip(ims, frame_sequences, strict=False):
            im.set_data(seq[i])
        return ims

    anim = animation.FuncAnimation(
        fig=fig,
        func=animate,
        frames=len(frame_sequences[0]),
        interval=interval,
        blit=True,
    )
    video_html = anim.to_html5_video()
    # Fit the video to the ReadTheDocs page width.
    video_html = video_html.replace(
        "<video ",
        '<video style="max-width:100%;height:auto;" ',
    )
    return HTML(video_html)


def overlay_tracks(
    images: list[np.ndarray],
    *,
    tracks_by_frame: dict[int, list[tuple[float, float, float, float, int, str]]],
    font_scale: float = 1.0,
    thickness: int = 1,
    box_thickness: int = 2,
) -> list[np.ndarray]:
    """Draw labeled, per-track colored boxes onto a copy of each RGB frame.

    ``images`` is a list of ``(H, W, 3)`` RGB frames. ``tracks_by_frame`` maps a
    frame index to a list of ``(x1, y1, x2, y2, track_id, label)`` tuples (an
    ``xyxy`` pixel box, an integer track id, and a display label). Each box is
    colored by its track id (see :func:`track_color`) and labeled with
    ``"{label} #{track_id}"`` in black text on a filled, track-colored
    background. Returns a new list of frames; the inputs are not modified.
    """

    def _track_color(track_id: int) -> tuple[int, int, int]:
        """Deterministic, high-saturation RGB color for a track ID."""
        hue = ((track_id * 37) % 180) / 180.0
        r, g, b = colorsys.hsv_to_rgb(h=hue, s=200 / 255, v=1.0)
        return int(r * 255), int(g * 255), int(b * 255)

    font = ImageFont.truetype(font_manager.findfont("DejaVu Sans"), size=max(8, round(font_scale * 24)))
    stroke = max(0, thickness - 1)  # thickness=1 -> normal weight (no stroke)
    pad = 3
    out: list[np.ndarray] = []
    for idx, image in enumerate(images):
        img = Image.fromarray(np.ascontiguousarray(image))  # RGB frame -> PIL image
        draw = ImageDraw.Draw(img)
        for x1, y1, x2, y2, track_id, label in tracks_by_frame.get(idx, []):
            color = _track_color(track_id)
            x1i, y1i, x2i, y2i = int(x1), int(y1), int(x2), int(y2)
            draw.rectangle((x1i, y1i, x2i, y2i), outline=color, width=box_thickness)

            # Label: black text on a filled box in the track color, for readability.
            text = f"{label} #{track_id}"
            left, top, right, bottom = draw.textbbox(xy=(0, 0), text=text, font=font, stroke_width=stroke)
            text_w, text_h = right - left, bottom - top
            box_top = max(0, y1i - text_h - 2 * pad)  # sit the label just above the box
            draw.rectangle(xy=(x1i, box_top, x1i + text_w + 2 * pad, box_top + text_h + 2 * pad), fill=color)
            draw.text(
                xy=(x1i + pad - left, box_top + pad - top),
                text=text,
                fill=(0, 0, 0),  # black text
                font=font,
                stroke_width=stroke,
                stroke_fill=(0, 0, 0),
            )
        out.append(np.array(img))
    return out
