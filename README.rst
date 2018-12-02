========================
opsdroid Skype extension
========================


This extension provides Skype support for opsdroid. To use, just add 'skype' to
the connectors section of your opsdroid config.

* Free software: Apache Software License 2.0

Configure it thus in your opsdroid config::

 connectors:
   - name: skype
     host: 0.0.0.0
     port: 9000
     app_id:
     app_pass:
     endpoint: /connectors/skype


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
