import json
import uuid
from typing import List, Dict

from apiclient import discovery
import httplib2
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client

import pandas as pd
import json
from record import FormRecords, ClientRecords, DoubleRecords
from GFClient import GoogleFormsApiClient
from access import ClientAccess

MAX_SIZE = 1000

DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )

def get_http(client_id, client_secret, access_token, refresh_token):
    credentials = client.OAuth2Credentials(
        access_token=access_token,  # set access_token to None since we use a refresh token
        client_id = client_id,
        client_secret = client_secret,
        refresh_token = refresh_token,
        token_expiry = None,
        token_uri = GOOGLE_TOKEN_URI,
        user_agent = None,
        revoke_uri = GOOGLE_REVOKE_URI
    )

    #credentials.refresh(httplib2.Http())  # refresh the access token (optional)
    #print(credentials.to_json())
    http = credentials.authorize(httplib2.Http()) 
    return http


class FormCache:
    def __init__(self):
        self.forms = dict()
        self.records = FormRecords()

    def exists(self, form_id):
        if form_id in self.forms:
            print('form in cache')
            return True
        else:
            return self.records.exists(form_id)

    def get(self, form_id):
        if form_id in self.forms:
            return self.forms[form_id]
        else:
            form = self.records.get(form_id)
            if form is not None:
                while len(self.forms) >= MAX_SIZE:
                    self.forms.popitem()
                self.forms[form_id] = form
            return form


    def add(self, form_id, form):
        self.records.add(form_id, form)

        if form_id in self.forms:
            self.forms[form_id] = form
        else:
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = form



class DoubleCache:
    def __init__(self):
        self.forms = dict()
        self.records = DoubleRecords()

    def exists(self, form_id):
        if form_id in self.forms:
            print('form in cache')
            return True
        else:
            return self.records.exists(form_id)

    def get(self, form_id):
        if form_id in self.forms:
            return self.forms[form_id]
        else:
            form = self.records.get(form_id)
            if form is not None:
                while len(self.forms) >= MAX_SIZE:
                    self.forms.popitem()
                self.forms[form_id] = form
            return form


    def add(self, form_id, form):
        self.records.add(form_id, form)

        if form_id in self.forms:
            self.forms[form_id] = form
        else:
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = form



class ClientCache:
    def __init__(self):
        self.forms = dict()
        self.records = ClientRecords()

    def exists(self, form_id):
        if form_id in self.forms:
            print('client in cache')
            return True
        else:
            return self.records.exists(form_id)

    def get(self, form_id):
        if form_id in self.forms:
            http = self.forms[form_id]
        else:
            http = self.records.get(form_id)
            if http is None:
                return None
                
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = http

        client = GoogleFormsApiClient(None)
        service = discovery.build('forms', 'v1', 
                    http=http, 
                    discoveryServiceUrl=DISCOVERY_DOC, 
                    static_discovery=False
                    )
        client.set_service(service)
        return client

    def add(self, form_id, client):
        json_service = get_json(client.service)
        #print(json_service.keys())
        json_request = json_service['_http']['request']['credentials']

        client_access = ClientAccess(json_request['client_id'], 
                json_request['client_secret'], 
                json_request['access_token'],
                json_request['refresh_token']
                )

        http = client_access.get_http()

        self.records.add(form_id = form_id, client = json_request)

        if form_id in self.forms:
            self.forms[form_id] = http
        else:
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = http



