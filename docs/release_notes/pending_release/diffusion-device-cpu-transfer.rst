* Fixed passing GPU-resident tensors to the MAITE augmentation wrappers, which used to
  raise ``TypeError: can't convert cuda:0 device type tensor to numpy``. Batch images,
  boxes, labels, and scores are now copied back to host memory first.

* Fixed ``DiffusionPerturber`` assuming its pipeline output was always safe to hand to
  ``numpy``. Tensor output is now moved off the compute device and converted to a
  channels-last ``uint8`` array, rounding rather than truncating to match how
  ``diffusers`` converts, and the pipeline is explicitly asked for PIL output.

* Fixed ``dataset_to_coco`` raising on GPU-resident datasets. Images, boxes, and labels are
  now copied back to host memory before export, so a MAITE dataset backed by a GPU
  dataloader can be written out directly.

* Documented the NVIDIA driver versions required to use a GPU with the ``diffusion``
  extra, including how to install a PyTorch build matching an older driver's CUDA
  version.

* Added a ``gpu`` factor to :file:`tox.ini` and a CI job running the ``diffusion-gpu``
  environment on every supported Python version, so the device-transfer paths are
  exercised on a real GPU. Every other test environment stays CPU-only. This also fixes
  the generative perturber notebook running on the CPU despite being scheduled on a GPU
  runner.

* Added a canary that fails when an environment requests a GPU that ``torch`` cannot use,
  so a GPU job with an unusable CUDA stack fails instead of quietly skipping every
  device-transfer test.
