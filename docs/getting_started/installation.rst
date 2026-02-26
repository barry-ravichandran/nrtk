Installation
============

.. tip::
  This page covers installation options beyond the basic
  PyPI/conda install shown in the :doc:`Getting Started </getting_started/quickstart>` section.

  **Not all perturbers are available with the base PyPI install** — many require optional
  third-party libraries such as pyBSM, OpenCV, or Pillow. With PyPI, you can
  selectively install only the extras that your workflow requires (see the
  :ref:`perturber-dependencies` table below). The conda-forge package includes all
  optional dependencies by default.

.. note::
   nrtk has been tested on Unix-based systems, including Linux, macOS, and WSL.

.. _pip:
.. _conda:

Installing nrtk
---------------

.. seealso::
  See :ref:`perturber-dependencies` below for the full list of optional extras
  and which perturbers they enable.

.. tab-set::

  .. tab-item:: pip

    nrtk can be installed via pip from `PyPI <https://pypi.org/project/nrtk/>`_.

    .. warning::
        The recommended way to install nrtk via ``pip`` is to use a virtual environment. To learn
        more, see `creating virtual environments in the Python Packaging User Guide
        <https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-virtual-environments>`_.

    .. prompt:: bash

        pip install nrtk[extra1,extra2,...]

  .. tab-item:: conda

    nrtk can be installed via conda from `conda-forge <https://github.com/conda-forge/nrtk-feedstock>`_.

    .. warning::
        The recommended way to install nrtk via ``conda`` is to use a virtual environment. To learn
        more, see `creating environments in the conda documentation
        <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands>`_.

    .. prompt:: bash

        conda install -c conda-forge nrtk

  .. tab-item:: From source

    Install from source with `Poetry`_ when you are contributing to nrtk, need to
    build the documentation locally, or want to run the test suite.

    .. warning::
      Poetry installation is only recommended for advanced nrtk users. For most users, pip or conda installation is
      sufficient.

    The following assumes `Poetry`_ is already installed. Otherwise, please refer to Poetry
    `installation`_ and `usage`_ before proceeding.

    .. note::
      nrtk requires Poetry 2.2 or higher.

    .. rubric:: About Poetry

    `Poetry`_ acts as a comprehensive tool for dependency management, virtual environment handling,
    and package building. It streamlines development by automating tasks like dependency resolution,
    ensuring consistent environments across different machines, and simplifying the packaging and
    publishing of Python projects. `Poetry`_ not only allows developers to install any extras they need,
    but also install multi-dependency groups like nrtk's docs, tests, and linting tools.

    **Be sure to note the following warning from Poetry's own documentation**:

    .. warning::
      Poetry should always be installed in a dedicated virtual environment to isolate it from the rest of your system.
      It should in no case be installed in the environment of the project that is to be managed by Poetry. This ensures
      that Poetry's own dependencies will not be accidentally upgraded or uninstalled. In addition, the isolated virtual
      environment in which poetry is installed should not be activated for running poetry commands.

    If unfamiliar with Poetry, take a moment to familiarize yourself using the above links, to ensure the smoothest
    introduction possible.

    .. rubric:: Clone and Install

    .. prompt:: bash

        cd /where/things/should/go/
        git clone https://github.com/kitware/nrtk.git ./
        poetry install

    .. rubric:: Installing Developer Dependencies

    The following installs both core and development dependencies as
    specified in the :file:`pyproject.toml` file, with versions specified
    (including for transitive dependencies) in the :file:`poetry.lock` file:

    .. prompt:: bash

        poetry sync --with linting,tests,docs

    .. note::
      Developers should also ensure their enviroment has Git LFS installed
      before their first commit. See the `Git LFS documentation <https://git-lfs.com/>`_
      for more details.

    .. rubric:: Installing Extras

    To install an extra group(s) to enable a perturbation, add the ``--extras`` flag to
    your install command, e.g.:

    .. prompt:: bash

        poetry sync --with linting,tests,docs --extras "extra1 extra2 ..."

    .. rubric:: Building the Documentation

    The documentation for NRTK is maintained as a collection of
    `reStructuredText`_ documents in the :file:`docs/` folder of the project.
    The :program:`Sphinx` documentation tool can process this documentation
    into a variety of formats, the most common of which is HTML.

    Within the :file:`docs/` directory is a Unix :file:`Makefile` (for Windows
    systems, a :file:`make.bat` file with similar capabilities exists).
    This :file:`Makefile` takes care of the work required to run :program:`Sphinx`
    to convert the raw documentation to an attractive output format.
    For example, calling the command below will generate
    HTML format documentation rooted at :file:`docs/_build/html/index.html`.

    .. prompt:: bash

        poetry run make html


    Calling the command ``make help`` here will show the other documentation
    formats that may be available (although be aware that some of them require
    additional dependencies such as :program:`TeX` or :program:`LaTeX`).

    .. seealso::
      Developers looking to contribute to NRTK should check out our
      `additional development resources </development>`_.

.. _perturber-dependencies:

Perturber Dependencies
----------------------
The following table lists each perturber and the extras required to use them. Install any
combination of extras as needed for your use case (e.g., ``pip install nrtk[pybsm,headless]``).

.. note::
   Perturbers that require OpenCV list ``graphics`` or ``headless`` as their extra.
   Use ``graphics`` for full GUI capabilities (``opencv-python``) or ``headless``
   for minimal, no-GUI environments (``opencv-python-headless``).
   The conda package includes all optional dependencies by default.

Photometric Perturbers
^^^^^^^^^^^^^^^^^^^^^^
.. dropdown:: Modify visual appearance (color, brightness, blur, noise)

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.photometric.blur.AverageBlurPerturber`
        - ``graphics`` or ``headless``
        - ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.photometric.enhance.BrightnessPerturber`
        - ``pillow``
        - ``Pillow``
      * - :class:`~nrtk.impls.perturb_image.photometric.enhance.ColorPerturber`
        - ``pillow``
        - ``Pillow``
      * - :class:`~nrtk.impls.perturb_image.photometric.enhance.ContrastPerturber`
        - ``pillow``
        - ``Pillow``
      * - :class:`~nrtk.impls.perturb_image.photometric.blur.GaussianBlurPerturber`
        - ``graphics`` or ``headless``
        - ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.photometric.noise.GaussianNoisePerturber`
        - ``skimage``
        - ``scikit-image``
      * - :class:`~nrtk.impls.perturb_image.photometric.blur.MedianBlurPerturber`
        - ``graphics`` or ``headless``
        - ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.photometric.noise.PepperNoisePerturber`
        - ``skimage``
        - ``scikit-image``
      * - :class:`~nrtk.impls.perturb_image.photometric.noise.SaltAndPepperNoisePerturber`
        - ``skimage``
        - ``scikit-image``
      * - :class:`~nrtk.impls.perturb_image.photometric.noise.SaltNoisePerturber`
        - ``skimage``
        - ``scikit-image``
      * - :class:`~nrtk.impls.perturb_image.photometric.enhance.SharpnessPerturber`
        - ``pillow``
        - ``Pillow``
      * - :class:`~nrtk.impls.perturb_image.photometric.noise.SpeckleNoisePerturber`
        - ``skimage``
        - ``scikit-image``

  .. seealso::
    For input requirements, see the
    :doc:`photometric perturber reference </reference/perturber_reference/photometric>`.

Geometric Perturbers
^^^^^^^^^^^^^^^^^^^^
.. dropdown:: Alter spatial positioning (rotation, scaling, cropping, translation)

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.geometric.random.RandomCropPerturber`
        - ---
        - ---
      * - :class:`~nrtk.impls.perturb_image.geometric.random.RandomRotationPerturber`
        - ``albumentations``, and (``graphics`` or ``headless``)
        - ``nrtk-albumentations``, ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.geometric.random.RandomScalePerturber`
        - ``albumentations``, and (``graphics`` or ``headless``)
        - ``nrtk-albumentations``, ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.geometric.random.RandomTranslationPerturber`
        - ---
        - ---

  .. seealso::
    For input requirements, see the
    :doc:`geometric perturber reference </reference/perturber_reference/geometric>`.

Environment Perturbers
^^^^^^^^^^^^^^^^^^^^^^

.. dropdown:: Simulate atmospheric effects (haze, water droplets)

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.environment.HazePerturber`
        - ---
        - ---
      * - :class:`~nrtk.impls.perturb_image.environment.WaterDropletPerturber`
        - ``waterdroplet``
        - ``scipy``, ``numba``

  .. seealso::
    For input requirements, see the
    :doc:`environment perturber reference </reference/perturber_reference/environment>`.

Optical Perturbers
^^^^^^^^^^^^^^^^^^

.. dropdown:: Model physics-based sensor and optical phenomena

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.optical.otf.CircularAperturePerturber`
        - ``pybsm``
        - ``pyBSM``
      * - :class:`~nrtk.impls.perturb_image.optical.otf.DefocusPerturber`
        - ``pybsm``
        - ``pyBSM``
      * - :class:`~nrtk.impls.perturb_image.optical.otf.DetectorPerturber`
        - ``pybsm``
        - ``pyBSM``
      * - :class:`~nrtk.impls.perturb_image.optical.otf.JitterPerturber`
        - ``pybsm``
        - ``pyBSM``
      * - :class:`~nrtk.impls.perturb_image.optical.PybsmPerturber`
        - ``pybsm``
        - ``pyBSM``
      * - :class:`~nrtk.impls.perturb_image.optical.radial_distortion_perturber.RadialDistortionPerturber`
        - ---
        - ---
      * - :class:`~nrtk.impls.perturb_image.optical.otf.TurbulenceAperturePerturber`
        - ``pybsm``
        - ``pyBSM``

  .. seealso::
    For input requirements, see the
    :doc:`optical perturber reference </reference/perturber_reference/optical>`.

Generative Perturbers
^^^^^^^^^^^^^^^^^^^^^

.. dropdown:: Model physics-based sensor and optical phenomena

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.generative.DiffusionPerturber`
        - ``diffusion``
        - ``torch``, ``diffusers``, ``accelerate``, ``Pillow``

  .. seealso::
    For input requirements, see the
    :doc:`generative perturber reference </reference/perturber_reference/generative>`.

Utility Perturbers
^^^^^^^^^^^^^^^^^^

.. dropdown:: Enable composition and third-party library integration

  .. list-table:: Perturber Dependencies
      :widths: 45 25 30
      :header-rows: 1

      * - Perturber
        - Extra(s) Required
        - Key Dependencies Provided by Extra(s)
      * - :class:`~nrtk.impls.perturb_image.AlbumentationsPerturber`
        - ``albumentations``, and (``graphics`` or ``headless``)
        - ``nrtk-albumentations``, ``OpenCV``
      * - :class:`~nrtk.impls.perturb_image.ComposePerturber`
        - ---
        - ---

  .. seealso::
    For input requirements, see the
    :doc:`utility perturber reference </reference/perturber_reference/utility>`.

.. _Poetry: https://python-poetry.org
.. _installation: https://python-poetry.org/docs/#installation
.. _usage: https://python-poetry.org/docs/basic-usage/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
