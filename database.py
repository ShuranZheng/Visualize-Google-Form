import json
import uuid
from typing import List, Dict

class FormQuestion:
    def __init__(self, questionId, title, options):
        self.questionId = questionId
        self.title = title
        self.answers = dict()
        for option in options:
            self.answers[option['value']] = 0
        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

    def update(self):
        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

class FormDatabase:
    """Class for loading data into BigQuery"""

    def __init__(self, form_id, forms, responses):
        self.responses = responses
        self.result = dict()

        questions = forms['items']
        for q in questions:
            title = q['title']
            if 'questionItem' in q:
                question = q['questionItem']['question']
                questionId = question['questionId']
                if 'choiceQuestion' in question:
                    options = question['choiceQuestion']['options']
                    formQ = FormQuestion(questionId = questionId, title = title, options = options)
                    self.result[questionId] = formQ

        for response in responses:
            self.add_response(response)


    def add_response(self, response):
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




