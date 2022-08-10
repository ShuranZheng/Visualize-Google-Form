import json
import uuid
from typing import List, Dict
from database import FormDatabase, DoubleQDatabase
from os.path import exists
from GFClient import GoogleFormsApiClient
from access import ClientAccess
import os

import httplib2
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client

import pandas as pd

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
    

class FormRecords:
    def __init__(self):
        self.forms = dict()
        if not os.path.exists('./records'):
            os.makedirs('./records')

        if exists('./records/formsID'):
            file = open('./records/formsID', 'r')
            self.forms = json.loads(file.read())


    def exists(self, form_id):
        if (form_id in self.forms) and (exists('./records/'+form_id)):
            print('form in records')
            return True
        else:
            return False

    def get(self, form_id):
        if form_id in self.forms:
            if exists('./records/'+form_id):
                file = open('./records/'+form_id, 'r')
                form = FormDatabase(form_id, None, None)
                data = json.loads(file.read())
                form.read(data)
                return form
        else:
            return None

    def add(self, form_id, form):
        if form_id not in self.forms:
            self.forms[form_id] = 0
            f = open('./records/formsID', 'w+')
            json.dump(self.forms, f)

        file = open('./records/'+form_id, 'w+')
        json.dump(get_json(form), file)

class DoubleRecords:
    def __init__(self):
        self.forms = dict()
        if not os.path.exists('./records'):
            os.makedirs('./records')

        if exists('./records/formsID'):
            file = open('./records/formsID', 'r')
            self.forms = json.loads(file.read())


    def exists(self, form_id):
        if (form_id in self.forms) and (exists('./records/double_'+form_id)):
            print('form in records')
            return True
        else:
            return False

    def get(self, form_id):
        if form_id in self.forms:
            if exists('./records/double_'+form_id):
                file = open('./records/double_'+form_id, 'r')
                form = DoubleQDatabase(form_id, None, None)
                data = json.loads(file.read())
                form.read(data)
                return form
        else:
            return None

    def add(self, form_id, form):
        if form_id not in self.forms:
            self.forms[form_id] = 0
            f = open('./records/formsID', 'w+')
            json.dump(self.forms, f)

        file = open('./records/double_'+form_id, 'w+')
        json.dump(get_json(form), file)



class ClientRecords:
    def __init__(self):
        self.forms = dict()
        if not os.path.exists('./records'):
            os.makedirs('./records')

        if exists('./records/formsID'):
            file = open('./records/formsID', 'r')
            self.forms = json.loads(file.read())


    def exists(self, form_id):
        if (form_id in self.forms) and (exists('./records/client_'+form_id)):
            print('client in records')
            return True
        else:
            return False

    def get(self, form_id):
        if form_id in self.forms:
            if exists('./records/client_'+form_id):
                file = open('./records/client_'+form_id, 'r')
                data = json.loads(file.read())

                client_access = ClientAccess(data['client_id'], 
                        data['client_secret'], 
                        data['access_token'],
                        data['refresh_token']
                        )

                http = client_access.get_http()

                return http
        else:
            return None

    def add(self, form_id, client):
        if form_id not in self.forms:
            self.forms[form_id] = 0
            f = open('./records/formsID', 'w+')
            json.dump(self.forms, f)

        file = open('./records/client_'+form_id, 'w+')
        json.dump(get_json(client), file)




