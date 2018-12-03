========================
opsdroid Skype extension
========================


This extension provides Skype support for `opsdroid`_. To use, just add 'skype' to
the connectors section of your opsdroid config. Here's an example opsdroid configuration for the connector::

 web:
     host: 0.0.0.0
     port: 9000
     
 connectors:
   - name: skype
     app_id:
     app_pass:
     endpoint: /connectors/skype

The connector will then be running at `http://0.0.0.0:9000/connectors/skype`. This is your skype bot endpoint.

To test the connector, you can use the `Bot Framework Emulator`_. This package includes a ready-made configuration file in `tests/bot.bot`.

To deploy a Skype bot, a Azure service account is needed. At the time of writing this (end of 2018), Azure offers a free tier that is sufficient to test the bot. To test and deploy the bot, create and configure a 'Bot Channels Registration' resource.

When configuring the bot in Azure, make sure to:

- enter the correct full 'Messaging endpoint' URL in settings
- test the bot (see 'Test in Web Chat')
- enter the bot Microsoft Application Id & Password into your opsdroid config; you may need to click the 'Manage' link in the bot registration settings to access the password
- add a Skype 'channel' to the registration resource (there is NO NEED to configure it in any way or publish it!)

After completing the above steps, visit your bot endpoint using a web browser; you will be redirected to a Microsoft-hosted
page for adding the bot as a Skype contact.

------------

Free software: Apache Software License 2.0

Package created with Cookiecutter_ using the `audreyr/cookiecutter-pypackage`_ project template.

.. _opsdroid: https://opsdroid.github.io
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _`Bot Framework Emulator`: https://docs.microsoft.com/en-us/azure/bot-service/bot-service-debug-emulator
