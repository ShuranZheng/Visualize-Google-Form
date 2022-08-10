import json
import uuid
from typing import List, Dict
from datetime import datetime, timedelta

import pandas as pd


def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )

class FormQuestion:
    def __init__(self, questionId, title, options):
        self.questionId = questionId
        self.title = title
        self.answers = dict()
        if options is not None:
            for option in options:
                self.answers[str(option['value'])] = 0

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


class DoubleQuestion:
    def __init__(self, questionIds,  title, options_one, options_two):
        self.questionIds = questionIds
        self.title = title
        self.answers = dict()
        #print(questionIds,  title, options_one, options_two)
        if options_one is not None:
            for option_one in options_one:
                if options_two is not None:
                    for option_two in options_two:
                        #print(type(self.answers), self.answers)
                        choiceID = str(option_one['value']) + ' / ' + str(option_two['value'])
                        self.answers[choiceID] = 0

        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

    def update(self):
        self.keys = list(self.answers.keys())
        self.values = list(self.answers.values())

    def read(self, data):
        if data is None:
            return

        self.questionIds = data['questionIds']
        self.title = data['title']
        self.answers = data['answers']
        self.keys = data['keys']
        self.values = data['values']


class DoubleQDatabase:

    def __init__(self, form_id, forms, responses):
        #self.responses = responses
        self.questionID = dict()
        self.result = dict()
        self.lastTime = None
        self.numRes = 0
        questions = None

        if forms is not None:
            questions = forms['items']

        if questions is not None:
            for q_one in questions:
                if q_one is not None:
                    title1 = str('1. ' + q_one['title'] +'\n')
                else:
                    title1 = None

                if 'questionItem' in q_one:
                    question_one = q_one['questionItem']['question']
                    qID_one = question_one['questionId']

                    if 'choiceQuestion' in question_one:
                        self.questionID[qID_one] = 0
                        options_one = question_one['choiceQuestion']['options']
                        for q_two in questions:
                            if q_two is not None:
                                title2 = str('2. ' + q_two['title'])
                                if 'questionItem' in q_two:
                                    question_two = q_two['questionItem']['question']
                                    qID_two = question_two['questionId']

                                    if ('choiceQuestion' in question_two) and (qID_one < qID_two):
                                        options_two = question_two['choiceQuestion']['options']
                                        questionIds = qID_one + qID_two

                                        formQ = DoubleQuestion(questionIds = questionIds, 
                                                title = title1 + title2, 
                                                options_one = options_one,
                                                options_two = options_two
                                                )
                                        self.result[questionIds] = formQ

        if responses is not None:
            for response in responses:
                self.add_response(response)


    def new_responses(self, responses):
        number = 0
        if responses is not None:
            for response in responses:
                print(get_json(response))
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

        for questionId_one in self.questionID:
            if (questionId_one in ans) and ('textAnswers' in ans[questionId_one]):
                choices_one = ans[questionId_one]['textAnswers']['answers']
    
                for questionId_two in self.questionID:
                    if (questionId_two in ans) and ('textAnswers' in ans[questionId_two]) and (questionId_one < questionId_two):
                        choices_two = ans[questionId_two]['textAnswers']['answers']
                        
                        for choice_one in choices_one:
                            for choice_two in choices_two:
                                questionIds = str(questionId_one) + str(questionId_two)
                                if questionIds in self.result:
                                    choiceID = str(choice_one['value']) + ' / ' + str(choice_two['value'])
                                    #print(self.result[questionIds].answers)
                                    #print('Add choiceID '+ str(choiceID))
                                    if choiceID in self.result[questionIds].answers:
                                        self.result[questionIds].answers[choiceID] += 1


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
        self.questionID = data['questionID']

        res = data['result']
        for questionId in res:
            formQ = DoubleQuestion(questionIds = None, 
                        title = None, 
                        options_one = None,
                        options_two = None
                        )
            formQ.read(res[questionId])
            self.result[questionId] = formQ





