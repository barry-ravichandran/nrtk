Testing & Evaluation Guides with MAITE
=======================================

Many robustness testing workflows benefit from using NRTK alongside other tools such as the
`JATIC <https://cdao.pages.jatic.net/public/>`_ program's
`Modular AI Trustworthy Engineering (MAITE) <https://github.com/mit-ll-ai-technology/maite>`_ toolbox. While NRTK
focuses on realistic image perturbations, MAITE provides a standardized interface for evaluating model performance
across a set of test conditions. Using these tools together enables modular, reproducible assessments of AI robustness
under simulated operational risks.

The following notebooks showcase how NRTK perturbations can be applied to simulate key operational risks within a
testing and evaluation (T&E) workflow. Each notebook illustrates potential impact on model performance, utilizing MAITE
as an evaluation harness.

----


Photometric Risks
-----------------

Perturbations that alter pixel intensity, color balance, or lighting conditions.

.. grid:: 1 2 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`light_mode` Extreme Illumination
      :class-card: sd-border-1

      Simulate brightness changes and evaluate model responses under lighting variability.

      +++

      .. button-ref:: /examples/maite/nrtk_brightness_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`auto_awesome` Lens Flare
      :class-card: sd-border-1

      Simulate a lens flare effect on an image and analyze its average and worst case effects on model precision.

      +++

      .. button-ref:: /examples/maite/nrtk_lens_flare_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

----


Geometric Risks
---------------

Perturbations that change spatial layout through rotation, scaling, or translation.

.. grid:: 1 2 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`crop_rotate` Affine Transformations
      :class-card: sd-border-1

      Explore how affine transformations affect model inputs and predictions.

      +++

      .. button-ref:: /examples/maite/nrtk_affine_perturbers_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

----


Environment Risks
-----------------

Perturbations that replicate weather and atmospheric visibility conditions.

.. grid:: 1 2 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`cloud` Fog / Haze
      :class-card: sd-border-1

      Evaluate model robustness under haze-like visibility conditions using synthetic perturbations.

      +++

      .. button-ref:: /examples/maite/nrtk_haze_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`water_drop` Rain / Water Droplets
      :class-card: sd-border-1

      Simulate a rain/water droplet effect and analyze its impact on model inputs and predictions.

      +++

      .. button-ref:: /examples/maite/nrtk_water_droplet_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

----


Optical Risks
-------------

Perturbations from sensor optics, camera physics, and atmospheric distortion.

.. grid:: 1 2 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`center_focus_weak` Visual Focus
      :class-card: sd-border-1

      Apply blur and focus distortions to test performance degradation from defocus.

      +++

      .. button-ref:: /examples/maite/nrtk_focus_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`photo_camera` Resolution & Noise
      :class-card: sd-border-1

      Explore how camera-specific transformations affect model inputs and predictions.

      +++

      .. button-ref:: /examples/maite/nrtk_sensor_transformation_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`vibration` Motion Jitter
      :class-card: sd-border-1

      Simulate camera motion jitter and assess its impact on image quality and model inference.

      +++

      .. button-ref:: /examples/maite/nrtk_jitter_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`waves` Atmospheric Turbulence
      :class-card: sd-border-1

      Simulate atmospheric distortion effects and assess its impact on image quality and model inference.

      +++

      .. button-ref:: /examples/maite/nrtk_turbulence_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

   .. grid-item-card:: :material-regular:`lens_blur` Radial Distortion
      :class-card: sd-border-1

      Simulate a radial distortion effect and analyze its impact on model inputs and predictions.

      +++

      .. button-ref:: /examples/maite/nrtk_radial_distortion_perturber_demo
         :color: primary
         :outline:
         :expand:

         Open Notebook →

----


Saliency Analysis
-----------------

Combining perturbations with model interpretability to understand *where* and *why* predictions change.

.. grid:: 1 2 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`visibility` Perturbations + Saliency
      :class-card: sd-border-1

      Integrate NRTK perturbations with saliency map generation to visualize how image changes affect model interpretation.

      +++

      .. button-ref:: /examples/maite/jatic-perturbations-saliency
         :color: primary
         :outline:
         :expand:

         Open Notebook →

.. toctree::
   :hidden:

   /examples/maite/nrtk_brightness_perturber_demo
   /examples/maite/nrtk_lens_flare_demo
   /examples/maite/nrtk_affine_perturbers_demo
   /examples/maite/nrtk_haze_perturber_demo
   /examples/maite/nrtk_water_droplet_perturber_demo
   /examples/maite/nrtk_focus_perturber_demo
   /examples/maite/nrtk_sensor_transformation_demo
   /examples/maite/nrtk_jitter_perturber_demo
   /examples/maite/nrtk_turbulence_perturber_demo
   /examples/maite/nrtk_radial_distortion_perturber_demo
   /examples/maite/jatic-perturbations-saliency
