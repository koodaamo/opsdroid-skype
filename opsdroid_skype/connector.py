import time
import json
import asyncio
import logging

import arrow
from httptools import HttpRequestParser
from http_parser.parser import HttpParser

# skype dependencies
from botbuilder.schema import (Activity, ActivityTypes)
from botframework.connector import ConnectorClient
from botframework.connector.auth import (MicrosoftAppCredentials, JwtTokenValidation, SimpleCredentialProvider)

# opsdroid dependencies
from opsdroid.connector import Connector
from opsdroid.message import Message


_LOGGER = logging.getLogger(__name__)
APP_ID = ""
APP_PASSWORD = ""

HOST = '127.0.0.1'
PORT = 9000


class SkypeConnector(Connector):

    def __init__(self, config):
        self.name = "SkypeConnector"
        self.config = config
        # self.default_room = "MyDefaultRoom" # The default room for messages to go
        self.loop = asyncio.get_event_loop()
        self.reader = self.writer = None
        self.credentials = MicrosoftAppCredentials(APP_ID, APP_PASSWORD)
        self.credential_provider = SimpleCredentialProvider(APP_ID, APP_PASSWORD)
        self.authenticated = False
        self.request_queue = asyncio.Queue()
        self.sequence = 0

    async def connect(self, opsdroid):
        self.server = await asyncio.start_server(self.accept, HOST, PORT)
        _LOGGER.info(_("Skype bot running at %s:%i"), HOST, PORT)

    async def accept(self, reader, writer):
        n = arrow.now()
        self.sequence += 1
        ts = '%i-%i-%i-%i' % (n.year, n.month, n.day, self.sequence)
        self.request_queue.put_nowait((reader, writer, ts))
        _LOGGER.debug("Skype bot queued request %s" % ts)


    async def listen(self, opsdroid):

        while True:

            reader, writer, ts = await self.request_queue.get()
            parser = HttpParser()

            while not parser.is_message_complete():
                data = await reader.read(1000)
                bytes_received = len(data)
                bytes_parsed = parser.execute(data, bytes_received)
                assert bytes_parsed == bytes_received

            body = parser.recv_body()
            msg = json.loads(str(body, 'utf-8'))
            activity = Activity.deserialize(msg)

            if not self.authenticated:
                _LOGGER.debug("Skype bot attempting to authenticate using message %s", ts)

                auth = parser.get_headers().get("Authorization")
                if not auth:
                    _LOGGER.warning("Skype bot received no Authorization header in msg %s", ts)
                try:
                    await JwtTokenValidation.authenticate_request(activity, auth, self.credential_provider)
                except:
                    _LOGGER.warning("Skype bot received invalid authentication message %s", ts)
                else:
                    self.authenticated = True
                    _LOGGER.debug("Skype bot handled authentication message %s", ts)
                continue

            if activity.type == ActivityTypes.conversation_update.value:
                if activity.members_added[0].id != activity.recipient.id:
                    _LOGGER.debug("Skype bot met new user in message %s", ts)
                    #reply = BotRequestHandler.__create_reply_activity(activity, 'Hello and welcome to the echo bot!')
                    #connector = ConnectorClient(self.credentials, base_url=reply.service_url)

            elif activity.type == ActivityTypes.message.value:
                connector = ConnectorClient(self.credentials, base_url=activity.service_url)
                orig = (activity, connector)
                msg = Message(activity.text, activity.from_property, activity.channel_id, self, orig)
                _LOGGER.debug("Skype bot parsed %s %s message %s", parser.get_method(), parser.get_url(), ts)
                await opsdroid.parse(msg)

            else:
                _LOGGER.warning("Skype bot got invalid message %s", ts)


    async def respond(self, message, opsdroid=None):
        "construct a Skype bot reply Activity and send it using the connector"

        request_activity, connector = message.raw_message

        reply = Activity(
            type=ActivityTypes.message,
            channel_id=request_activity.channel_id,
            conversation=request_activity.conversation,
            recipient=request_activity.from_property,
            from_property=request_activity.recipient,
            text=message.text,
            service_url=request_activity.service_url)

        connector.conversations.send_to_conversation(reply.conversation.id, reply)


    async def disconnect(self, opsdroid):
        "Close the Skype bot server"

        self.server.close()
        await self.server.wait_closed()
