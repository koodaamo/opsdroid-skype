========================
opsdroid Skype extension
========================


This extension provides Skype support for opsdroid. To use, just add 'skype' to
the connectors section of your opsdroid config.

* Free software: Apache Software License 2.0

Example opsdroid configuration for the connector::

 web:
     host: 0.0.0.0
     port: 9000
     
 connectors:
   - name: skype
     app_id:
     app_pass:
     endpoint: /connectors/skype

The connector will then be running at `http://0.0.0.0:9000/connectors/skype`. This is your skype bot endpoint.

To test the connector, you can use the `Bot Framework Emulator`. This package includes a ready-made configuration file in `tests/bot.bot`.

To deploy a Skype bot, a Azure service account is needed. At the time of writing this (end of 2018), Azure offers a free tier that is sufficient to test the bot. The main steps to take in Azure to deploy the bot are:

* create a 'Bot Channels Registration' resource
* configure the registration (see 'settings')
   * make sure to enter the correct full 'Messaging endpoint' URL (see above ^)
   * test the bot using Azure (see 'Test in Web Chat')
   * get a MS app id & password (you may need to click 'manage' in the settings view to get the password), and then enter those into the opsdroid config (see above ^ example)
   * add a Skype 'channel' to the registration (note: there is NO NEED to configure it in any way)
* visit your opsdroid bot URL using any web browser. You will see a button 



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Bot Framework Emulator`: https://docs.microsoft.com/en-us/azure/bot-service/bot-service-debug-emulator
