import json
import uuid
from typing import List, Dict

import pandas as pd

MAX_SIZE = 10000

class FormCache:
    def __init__(self):
        self.forms = dict()

    def exists(self, form_id):
        if form_id in self.forms:
            return True
        else:
            return False

    def get(self, form_id):
        if form_id in self.forms:
            return self.forms[form_id]
        else:
            return None

    def add(self, form_id, form):
        if form_id in self.forms:
            self.forms[form_id] = form
        else:
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = form

class ClientCache:
    def __init__(self):
        self.forms = dict()

    def exists(self, form_id):
        if form_id in self.forms:
            return True
        else:
            return False

    def get(self, form_id):
        if form_id in self.forms:
            return self.forms[form_id]
        else:
            return None

    def add(self, form_id, form):
        if form_id in self.forms:
            self.forms[form_id] = form
        else:
            while len(self.forms) >= MAX_SIZE:
                self.forms.popitem()
            self.forms[form_id] = form



