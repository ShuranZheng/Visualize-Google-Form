from typing import List, Dict


from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
import json


class GoogleFormsApiClient:
    """Class for interacting with Google Forms API"""

    SCOPES = [
        "https://www.googleapis.com/auth/forms.body.readonly",
        "https://www.googleapis.com/auth/forms.responses.readonly"
    ]

    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    def __init__(self):
        self.store = file.Storage('token.json')
        self.flow = client.flow_from_clientsecrets('client_secret.json', self.SCOPES)
        self.creds = tools.run_flow(self.flow, self.store)
        self.service = discovery.build('forms', 'v1', http=self.creds.authorize(Http()), discoveryServiceUrl=self.DISCOVERY_DOC, static_discovery=False)


    def get_forms_questions(self, form_id) -> dict:
        request = self.service.forms().get(formId=form_id).execute()
        return request


    def get_forms_responses(self, form_id) -> List[Dict]:
        responses = list()
        request = self.service.forms().responses().list(formId=form_id, pageToken=None)

        while request is not None:
            response = request.execute()
            responses = responses + response.get('responses', [])
            request = self.service.forms().responses().list_next(request, response)

        return responses
