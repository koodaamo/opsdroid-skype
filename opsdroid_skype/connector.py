import time
import json
import asyncio
import logging

import aiohttp
import arrow

# skype dependencies
from botbuilder.schema import (Activity, ActivityTypes)
from botframework.connector import ConnectorClient
from botframework.connector.auth import (MicrosoftAppCredentials, JwtTokenValidation, SimpleCredentialProvider)

# opsdroid dependencies
from opsdroid.connector import Connector
from opsdroid.message import Message


_LOGGER = logging.getLogger("skypeconnector")

# authentication
APP_ID = ""
APP_PASS = ""

# server configuration
ENDPOINT = "/connector/skype"


class SkypeConnector(Connector):

    def __init__(self, config):
        self.name = self.__class__.__name__
        self.loop = asyncio.get_event_loop()
        self.config = config
        self.endpoint = config.get("endpoint", ENDPOINT)
        self.app_id = config.get("app_id", APP_ID)
        self.app_pass = config.get("app_pass", APP_PASS)
        self.credentials = MicrosoftAppCredentials(self.app_id, self.app_pass)
        self.credential_provider = SimpleCredentialProvider(self.app_id, self.app_pass)
        self.authenticated = False
        self.counter = 0
        self.queue = asyncio.Queue() # message queue

    @property
    def authentication_required(self):
        "only require authentication if credentials are supplied"
        return True if self.app_id and self.app_pass else False

    async def connect(self, opsdroid):
        "start up the connector"
        self.opsdroid = opsdroid
        router = opsdroid.web_server.web_app.router
        opsdroid.web_server.web_app.router.add_post(self.endpoint, self.handle_POST)
        opsdroid.web_server.web_app.router.add_get(self.endpoint, self.handle_GET)
        opsdroid.web_server.web_app.router.add_options(self.endpoint, self.handle_OPTIONS)
        _LOGGER.debug("inbound connector listening at %s" % self.endpoint)


    async def handle_OPTIONS(self, request):
        "the Azure test web chat makes HTTP OPTIONS calls to bot"
        _LOGGER.debug("received OPTIONS request")
        return aiohttp.web.Response(text="", status=200)

    async def handle_GET(self, request):
        _LOGGER.debug("received GET request")
        return aiohttp.web.HTTPFound('https://join.skype.com/bot/' + self.app_id)

    async def handle_POST(self, request):
        "main handler; all bot communications happens over HTTP POST"

        # set up a timestamp and counter
        n = arrow.now()
        self.counter += 1
        ts = '%i-%i-%i-%i' % (n.year, n.month, n.day, self.counter)

        # parse into Activity
        jsonmsg = await request.json()
        activity = Activity.deserialize(jsonmsg)

        # try to authenticate if required
        if not self.authenticated and self.authentication_required:
            result = await self.authenticate(request, activity)
            if result == False:
                return aiohttp.web.Response(text="Bot could not authenticate", status=401)

        # handle different activities
        if activity.type == ActivityTypes.conversation_update.value:
            self.handle_join(activity)
        elif activity.type == ActivityTypes.message.value:
            connector = ConnectorClient(self.credentials, base_url=activity.service_url)
            orig = (activity, connector)
            msg = Message(activity.text, activity.from_property, activity.channel_id, self, orig)
            self.queue.put_nowait(msg)
            _LOGGER.debug("queued message")
        else:
            _LOGGER.warning("got invalid activity in message %s: %s", ts, activity.name)
            _LOGGER.debug(activity)
            _LOGGER.debug(jsonmsg)

        return aiohttp.web.Response(text="OK", status=200)


    async def authenticate(self, request, activity):
        ""
        authh = request.headers.get("Authorization")
        if authh:
            try:
                await JwtTokenValidation.authenticate_request(activity, authh, self.credential_provider)
            except:
                _LOGGER.warning("attempted to authenticate but received invalid authentication message")
                return False
            else:
                self.authenticated = True
                _LOGGER.debug("authenticated")
                return True
        else:
            _LOGGER.warning("not authenticated and no Authorization header")
            return False


    def handle_join(self, activity):
        "process channel joins"

        if activity.members_added[0].id != activity.recipient.id:
            _LOGGER.info("new user joined chat")
        else:
            _LOGGER.info("we were added to chat")


    async def listen(self, opsdroid):
        "Listen (queue) for new messages"
        while True:
            try:
                msg = await self.queue.get()
            except RuntimeError:
                break
            result = await self.opsdroid.parse(msg)
            self.queue.task_done()


    async def respond(self, message, opsdroid=None):
        request_activity, connector = message.raw_message

        reply = Activity(
            type=ActivityTypes.message,
            channel_id=request_activity.channel_id,
            conversation=request_activity.conversation,
            recipient=request_activity.from_property,
            from_property=request_activity.recipient,
            text=message.text,
            service_url=request_activity.service_url)

        def send_response():
            connector.conversations.send_to_conversation(reply.conversation.id, reply)

        result = await self.loop.run_in_executor(None, send_response)
        _LOGGER.debug("response sent")

    async def disconnect(self, opsdroid):
        await self.queue.join()

