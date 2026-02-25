Saliency Analysis with XAITK-Saliency
=====================================

While NRTK focuses on realistic image perturbations to reveal model degradation at the evaluation level, it is just as
important to investigate **why** this performance degradation may be occuring. A workflow combining NRTK with
`XAITK-Saliency <https://github.com/XAITK/xaitk-saliency>`_ enables this analysis by generating saliency maps which
reveal how model focus changes as perturbations are varied.


The following notebooks showcase this workflow for both image classification and object detection. After completing
these tutorials, you'll be able to:

- Apply systematic perturbations and generate interpretable saliency maps.
- Recognize robust vs. sensitive model behaviors as you test.
- Quantify saliency changes and understand what they indicate.
- Make informed decisions about model deployment and improvement.


.. grid:: 1 1 2 2
   :gutter: 3
   :padding: 2 2 0 0

   .. grid-item-card:: :material-regular:`image` Classification + Saliency
      :link: /examples/nrtk_xaitk_workflow/image_classification_perturbation_saliency
      :link-type: doc

      Combine perturbations with XAITK saliency maps to understand
      classification model behavior under degradation.

   .. grid-item-card:: :material-regular:`center_focus_strong` Detection + Saliency
      :link: /examples/nrtk_xaitk_workflow/object_detection_perturbation_saliency
      :link-type: doc

      Extend the saliency workflow to object detection, visualizing
      shifts in detector attention and bounding boxes.

.. toctree::
   :hidden:

   /examples/nrtk_xaitk_workflow/image_classification_perturbation_saliency
   /examples/nrtk_xaitk_workflow/object_detection_perturbation_saliency
