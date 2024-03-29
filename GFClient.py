from typing import List, Dict
from concurrent.futures import TimeoutError

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from google.cloud import pubsub_v1
from googleapiclient.errors import HttpError

import json
import httplib2
import logging
import sys

def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
        )

class GoogleFormsApiClient:

    SCOPES = [
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/forms.responses.readonly",
    ]

    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    project_id = "Shuran"
    topic_id = "gforms"
    subscription_id = "gforms-sub"
    timeout = 5.0

    def __init__(self, form_id):
        if form_id is None:
            self.store = None
            self.flow = None
            self.creds = None
            self.service = None
            
        else:
            self.store = file.Storage('token.json')
            self.flow = client.flow_from_clientsecrets('client_secret.json', self.SCOPES)
            self.creds = tools.run_flow(self.flow, self.store)
            #print(get_json(self.creds.authorize(Http())))

            httplib2.debuglevel = 4
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logger.addHandler(logging.StreamHandler(sys.stdout))


            self.service = discovery.build('forms', 'v1', 
                    http=self.creds.authorize(Http()), 
                    discoveryServiceUrl=self.DISCOVERY_DOC, 
                    static_discovery=False
                    )
            #print(get_json(self.service))

            #http = Http()
            #json_service = get_json(self.service)
            #http.request = json_service['_http']['request']
            #print(get_json(http))

            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(self.project_id, self.topic_id)

            #topic = publisher.create_topic(request={"name": topic_path})

            watch = {
                "watch": {
                    "target": {
                        "topic": {
                            "topicName": topic_path
                        }
                    },
                "eventType": "RESPONSES"
                }
            }

            #result = self.service.forms().watches().create(formId=form_id, body=watch).execute()
            
            try:
                result = self.service.forms().watches().create(formId=form_id, 
                    body=watch).execute()
            except HttpError as e:
                print(e._get_reason())

            #AllWatches = self.service.forms().watches().list(formId=form_id).execute()
            #print(AllWatches)

    def set_service(self, service):
        self.service = service

    def get_forms_questions(self, form_id) -> dict:
        request = self.service.forms().get(formId=form_id).execute()
        return request


    def get_forms_responses(self, form_id, timestamp) -> List[Dict]:
        responses = list()
        request = self.service.forms().responses().list(formId=form_id, 
            filter=timestamp, 
            pageToken=None
            )

        while request is not None:
            response = request.execute()
            responses = responses + response.get('responses', [])
            request = self.service.forms().responses().list_next(request, response)

        return responses
