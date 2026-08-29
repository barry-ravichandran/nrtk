.. _{{ fullname }}:

{{ objname }}
-----------------------------------------------------

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}
   :members:
   :special-members:
   :exclude-members: __init_subclass__, __new__
{% block methods %}
{% if methods %}

   .. rubric:: {{ _('Methods') }}

   .. autosummary::
      :nosignatures:

{% for item in methods %}
      {%- if not item.startswith('_') %}
      ~{{ name }}.{{ item }}
      {%- endif -%}
{%- endfor %}
{% endif %}
{%- endblock %}
