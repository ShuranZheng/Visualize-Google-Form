import json
import uuid
from typing import List, Dict

import pandas as pd
import json
from record import FormRecords

MAX_SIZE = 1000

def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )

class FormCache:
    def __init__(self):
        self.forms = dict()
        self.records = FormRecords()

    def exists(self, form_id):
        if form_id in self.forms:
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



