* Renamed the ``pre-commit`` tox environment to ``precommit``, so it is run with
  ``tox -e precommit``. tox splits environment names on hyphens into factors, so the
  hyphenated name was never a literal name and only matched dependency conditionals as
  the factors ``pre`` and ``commit``. The GitLab quality job was renamed to match.
