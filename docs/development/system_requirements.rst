===================
System Requirements
===================

This page documents the **supported architectures** and **recommended minimum
hardware** for NRTK in both its forms: the ``nrtk`` Python library and the
``nrtk-perturber`` container. Requirements are largely the same for both forms
and are described together, with differences called out explicitly.

.. note::
   Hardware figures below are rough order-of-magnitude estimates intended to
   cover the *minimum to function* plus a *recommended* configuration for
   comfortable use. Actual needs depend on image size, dataset size, the number
   of perturbation parameter combinations, and which perturbers you use.

Supported Architectures
=======================

Python library (``nrtk``)
-------------------------
* **Python:** CPython 3.10 – 3.14.
* **Operating systems:** Linux, macOS, and Windows via WSL. (NRTK is tested on
  Unix-based systems; native Windows is not supported.)

Container (``nrtk-perturber``)
------------------------------
* **Architecture:** ``linux/amd64`` (``x86_64``) **only**.
* **Bundled Python:** the image is built on an official ``python`` base image and
  installs all optional extras.

Recommended Minimum Hardware
============================

.. important::
   **Memory is the limiting factor on dataset size for batch perturbation.**
   ``nrtk-perturber`` accumulates the entire perturbed output dataset(s) in
   memory before writing them to disk, so peak RAM scales roughly with
   *(decoded image bytes in the dataset)* × *(number of perturbation parameter
   combinations)*. For large datasets or many parameter combinations, partition
   the dataset or reduce the number of combinations to stay within available RAM.

.. list-table::
   :header-rows: 1
   :widths: 14 22 22 22 22

   * - Resource
     - Library, classical perturbers only
     - Library, with ``diffusion``
     - Container
     - Notes
   * - CPU
     - 2 cores min, 4+ recommended
     - 4–8 cores recommended
     - 4–8 cores recommended
     - pyBSM and water-droplet perturbers use Numba JIT and scale with cores;
       CPU diffusion benefits strongly from more cores.
   * - GPU
     - None
     - Optional NVIDIA CUDA, ≥ 6–8 GB VRAM
     - None
     - Container is CPU-only. Diffusion perturber supports CPU fallback but is slow.
       See :ref:`gpu-driver-compatibility` for the required NVIDIA driver version.
   * - Memory (RAM)
     - 2 GB min, 4 GB recommended
     - 8–16 GB recommended
     - 8–16 GB recommended
     - The diffusion model loads fully into memory (~a few GB). See the
       data-size note below.
   * - Storage
     - ~0.5 GB install
     - ~3–6 GB (PyTorch + diffusers + model cache)
     - ~3–6 GB (PyTorch + diffusers + model cache)
     - First diffusion use downloads ``timbrooks/instruct-pix2pix`` (~a few GB)
       to the Hugging Face cache (``~/.cache/huggingface``). The container image
       itself is several GB.


.. _gpu-driver-compatibility:

GPU Driver and CUDA Compatibility
=================================

Extras that install PyTorch, such as ``diffusion``, take it from PyPI, whose Linux
wheels bundle their own CUDA runtime. That runtime has to be supported by the
installed NVIDIA driver, so the driver — not NRTK — determines which PyTorch
releases can use the GPU. Newer PyTorch releases bundle newer CUDA runtimes and
need newer drivers; PyTorch's `install matrix
<https://pytorch.org/get-started/locally/>`_ and NVIDIA's `CUDA compatibility
guide <https://docs.nvidia.com/deploy/cuda-compatibility/>`_ carry the current
mapping.

NRTK requires ``torch>=2.10.0`` and intentionally sets no upper bound, so a fresh
install resolves to the newest PyTorch release. Selecting a CUDA build is left to
the installing environment, which is the convention for libraries that depend on
PyTorch.

When the driver is older than the bundled runtime requires, CUDA cannot
initialize: ``torch.cuda.is_available()`` returns ``False`` even though
``nvidia-smi`` lists a GPU, and
:class:`~nrtk.impls.perturb_image.generative.DiffusionPerturber` warns
``CUDA is not available, but was requested. Falling back to CPU.`` before running
on the CPU. The symptom looks like a missing GPU rather than a driver mismatch.

To use the GPU on such a host, either update the NVIDIA driver, or install a
PyTorch build matching the driver's CUDA version from the PyTorch index:

.. code-block:: bash

   # Replace cuXXX with the CUDA version the driver supports, e.g. cu128.
   pip install torch --index-url https://download.pytorch.org/whl/cuXXX

Run ``nvidia-smi`` to see the installed driver and the highest CUDA version it
supports.
