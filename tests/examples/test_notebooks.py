from importlib.util import find_spec

import pytest

from nrtk.utils._exceptions import NotebookTestingImportError

from .test_notebook_utils import list_error_messages, pyright_analyze

deps = ["jupytext"]
specs = [find_spec(dep) for dep in deps]
is_usable = all(spec is not None for spec in specs)


@pytest.mark.skipif(not is_usable, reason=str(NotebookTestingImportError()))
class TestPyrightNotebook:
    @pytest.mark.filterwarnings("ignore:Jupyter is migrating its paths")
    @pytest.mark.parametrize(
        ("filepath", "expected_num_errors"),
        [
            ("docs/examples/maite/gradio/nrtk-gradio.ipynb", 0),
            ("docs/examples/maite/augmentations.ipynb", 0),
            ("docs/examples/maite/jatic-perturbations-saliency.ipynb", 0),
            ("docs/examples/maite/nrtk_brightness_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_haze_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_focus_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_sensor_transformation_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_lens_flare_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_translation_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_turbulence_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_water_droplet_perturber_demo.ipynb", 0),
            ("docs/examples/maite/nrtk_radial_distortion_perturber_demo.ipynb", 0),
            ("docs/examples/pybsm/pybsm_test.ipynb", 0),
            ("docs/examples/coco_scorer.ipynb", 0),
            ("docs/examples/nrtk_tutorial.ipynb", 0),
            ("docs/examples/otf_visualization.ipynb", 0),
            ("docs/examples/perturbers.ipynb", 0),
            ("docs/examples/simple_generic_generator.ipynb", 0),
            ("docs/examples/simple_pybsm_generator.ipynb", 0),
            ("docs/examples/albumentations_perturber.ipynb", 0),
        ],
    )
    def test_pyright_nb(self, filepath: str, expected_num_errors: int) -> None:
        results = pyright_analyze(filepath)  # type: ignore
        assert results["summary"]["errorCount"] <= expected_num_errors, list_error_messages(results)  # type: ignore
