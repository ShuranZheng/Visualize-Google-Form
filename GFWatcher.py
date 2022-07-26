from typing import List, Dict
from concurrent.futures import TimeoutError

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from google.cloud import pubsub_v1

import json

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"Received {message}.")
    message.ack()

class GoogleFormsWatcher:

    SCOPES = [
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.responses.readonly",
    ]

    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    project_id = "Shuran"
    topic_id = "gforms"
    subscription_id = "gforms-sub"
    timeout = 5.0

    def __init__(self, form_id):

        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(self.project_id, self.subscription_id)

        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        print(f"Listening for messages on {subscription_path}..\n")

        # Wrap subscriber in a 'with' block to automatically call close() when done.
        with subscriber:
            try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
                streaming_pull_future.result(timeout=self.timeout)
            except TimeoutError:
                streaming_pull_future.cancel()  # Trigger the shutdown.
                streaming_pull_future.result()  # Block until the shutdown is complete.

