import json
import uuid
from typing import List, Dict
from datetime import datetime, timedelta

import pandas as pd


class FormQuestion:
    def __init__(self, questionId, title, options):
        self.questionId = questionId
        self.title = title
        self.answers = dict()
        if options is not None:
            for option in options:
                self.answers[option['value']] = 0

        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

    def update(self):
        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

    def read(self, data):
        if data is None:
            return

        self.questionId = data['questionId']
        self.title = data['title']
        self.answers = data['answers']
        self.keys = data['keys']
        self.values = data['values']


class FormDatabase:

    def __init__(self, form_id, forms, responses):
        #self.responses = responses
        self.result = dict()
        self.lastTime = None
        self.numRes = 0
        questions = None

        if forms is not None:
            questions = forms['items']

        if questions is not None:
            for q in questions:
                if q is not None:
                    title = q['title']
                else:
                    title = None

                if 'questionItem' in q:
                    question = q['questionItem']['question']
                    questionId = question['questionId']

                    if 'choiceQuestion' in question:
                        options = question['choiceQuestion']['options']
                        formQ = FormQuestion(questionId = questionId, 
                                title = title, 
                                options = options
                                )
                        self.result[questionId] = formQ

        if responses is not None:
            for response in responses:
                self.add_response(response)


    def new_responses(self, responses):
        number = 0
        if responses is not None:
            for response in responses:
                self.add_response(response)
                number = number + 1
        return number


    def add_response(self, response):
        if response is None:
            return

        self.numRes = self.numRes + 1

        if self.lastTime is None:
            self.lastTime = response['lastSubmittedTime']
        else:
            if response['lastSubmittedTime'] > self.lastTime:
                self.lastTime = response['lastSubmittedTime']

        ans = response['answers']

        for questionId in self.result:
            if (questionId in ans) and ('textAnswers' in ans[questionId]):
                choices = ans[questionId]['textAnswers']['answers']

                for choice in choices:
                    self.result[questionId].answers[choice['value']] += 1


    def get_result(self):
        for questionId in self.result:
            self.result[questionId].update()

        return self.result


    def read(self, data):
        if data is None:
            return

        self.result = dict()
        self.lastTime = data['lastTime']
        self.numRes = data['numRes']

        res = data['result']
        for questionId in res:
            formQ = FormQuestion(questionId = None, 
                        title = None, 
                        options = None
                        )
            formQ.read(res[questionId])
            self.result[questionId] = formQ





