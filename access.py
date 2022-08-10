import json
import uuid
from typing import List, Dict

from apiclient import discovery
import httplib2
from oauth2client import GOOGLE_REVOKE_URI, GOOGLE_TOKEN_URI, client

import pandas as pd
import json
from GFClient import GoogleFormsApiClient

class ClientAccess:
    def __init__(self, client_id, client_secret, access_token, refresh_token):
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.refresh_token = None
        if client_id is not None:
            self.client_id = client_id
        if client_secret is not None:
            self.client_secret = client_secret
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token

    def get_http(self):
        credentials = client.OAuth2Credentials(
            access_token=self.access_token,  # set access_token to None since we use a refresh token
            client_id = self.client_id,
            client_secret = self.client_secret,
            refresh_token = self.refresh_token,
            token_expiry = None,
            token_uri = GOOGLE_TOKEN_URI,
            user_agent = None,
            revoke_uri = GOOGLE_REVOKE_URI
        )

        #credentials.refresh(httplib2.Http())  # refresh the access token (optional)
        #print(credentials.to_json())
        http = credentials.authorize(httplib2.Http()) 
        return http

