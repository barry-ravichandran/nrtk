from collections.abc import Generator, Iterator
from itertools import chain
from typing import BinaryIO

import av
from av.filter import Graph
from av.video.frame import VideoFrame as AVVideoFrame
from av.video.reformatter import VideoReformatter

from nrtk.interfaces import VideoFrame

# swscale flags that force a bit-exact, architecture-independent YUV->RGB conversion.
# Plain "bitexact" is NOT sufficient on its own; the chroma upsampling (e.g. yuv420p -> rgb)
# still diverges by a gray level or two between arm64 and x86_64 SIMD paths. Adding
# full_chroma_int + accurate_rnd pins the chroma interpolation and rounding to the reference
# implementation so the decoded pixels are identical on every CPU. Required for byte-exact
# video regression snapshots to be portable across the (arm64) dev machines and (x86_64) CI.
_BITEXACT_SWS_FLAGS = "bitexact+full_chroma_int+accurate_rnd"


def _bitexact_rgb_graph(template: AVVideoFrame) -> Graph:
    """Build a filtergraph that converts decoded frames to bit-exact rgb24.

    PyAV's ``VideoReformatter`` does not expose the swscale flags, so the conversion is
    done through a ``scale`` filter (which does) followed by ``format=rgb24``.
    """
    graph = Graph()
    buffer = graph.add_buffer(
        width=template.width,
        height=template.height,
        format=template.format,
        time_base=template.time_base,
    )
    scale = graph.add(filter="scale", args=f"flags={_BITEXACT_SWS_FLAGS}")
    fmt = graph.add(filter="format", args="rgb24")
    sink = graph.add(filter="buffersink")
    buffer.link_to(scale)
    scale.link_to(fmt)
    fmt.link_to(sink)
    graph.configure()
    return graph


def read_video(
    file: str | BinaryIO,
    format_name: str | None = None,
    *,
    bitexact: bool = False,
) -> Generator[VideoFrame, None, None]:
    """Decodes a video stream.

    Args:
        file:
            Filename or bytestream containing video to be read.
        format_name:
            Name of video format (e.g. "mp4") in case it cannot be determined from the file parameter.
        bitexact:
            If True, perform the YUV->RGB conversion with bit-exact swscale flags so the decoded
            pixels are identical across CPU architectures. Use this when decoding an input whose
            frames feed a byte-exact regression snapshot; otherwise the default (faster, SIMD)
            path is used.

    Returns:
        Generator yielding video frames as they are read from file.
    """
    video = av.open(file, mode="r", format=format_name)
    if bitexact:
        graph = None
        for raw_frame in video.decode(video=0):
            if graph is None:
                graph = _bitexact_rgb_graph(raw_frame)
            graph.push(raw_frame)
            frame_image = graph.pull().to_ndarray()
            yield VideoFrame(image=frame_image, timestamp=raw_frame.time)
        video.close()
        return

    frame_converter = VideoReformatter()
    for raw_frame in video.decode(video=0):
        frame_image = frame_converter.reformat(raw_frame, format="rgb24").to_ndarray()
        yield VideoFrame(image=frame_image, timestamp=raw_frame.time)

    video.close()


def write_video(file: str | BinaryIO, frames: Iterator[VideoFrame], format_name: str | None = None) -> None:
    """Encodes a lossless video stream.

    Args:
        file:
            Filename or bytestream to write encoded video to.
        frames:
            Video frames to encode.
        format_name:
            Name of video format (e.g. "mp4") in case it cannot be determined from the file parameter.
    """
    try:
        first_frame = next(frames)
    except StopIteration:
        return

    video = av.open(file, mode="w", format=format_name)
    x265_params = {
        "log-level": "warning",
        "lossless": "1",
    }
    options = {
        "x265-params": ":".join(key + "=" + value for key, value in x265_params.items()),
    }

    video.add_stream("libx265", options=options)
    video_stream = video.streams.video[0]
    video_stream.width = first_frame.image.shape[1]
    video_stream.height = first_frame.image.shape[0]
    video_stream.codec_context.pix_fmt = "yuv444p"
    video_stream.codec_context.thread_count = 0
    video_stream.codec_context.thread_type = "AUTO"

    video.start_encoding()
    assert video_stream.time_base is not None
    video_stream.codec_context.time_base = video_stream.time_base
    time_base = float(video_stream.time_base)

    frame_converter = VideoReformatter()
    for frame in chain([first_frame], frames):  # noqa: FKA100 - keyword arguments don't make sense for chain()
        frame_rgb = AVVideoFrame.from_ndarray(array=frame.image, format="rgb24")
        frame_rgb.pts = round(frame.timestamp / time_base)
        frame_rgb.time_base = video_stream.time_base
        frame_yuv = frame_converter.reformat(frame_rgb, format=video_stream.format.name)
        packets = video_stream.codec_context.encode(frame_yuv)
        video.mux(packets)

    # Flush encoder — H.265 buffers frames internally for compression.
    # Without this, buffered frames are silently discarded on close.
    packets = video_stream.codec_context.encode(None)
    video.mux(packets)

    video.close()
