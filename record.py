import json
import uuid
from typing import List, Dict
from database import FormDatabase
from os.path import exists
import os

import pandas as pd

def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
        )

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





