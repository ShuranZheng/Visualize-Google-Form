from flask import Flask, request, redirect, url_for
from flask import current_app as app
from flask import render_template

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from typing import List, Dict
from datetime import datetime

from GFClient import GoogleFormsApiClient
from GFWatcher import GoogleFormsWatcher
from database import FormDatabase, DoubleQDatabase
from cache import FormCache, ClientCache, DoubleCache
import json
import logging
import httplib2
import sys

httplib2.debuglevel = 4

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

formCache = FormCache()
doubleCache = DoubleCache()
clientCache = ClientCache()

def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == 'POST':
		#print(request.form['formID'])
		formID = request.form['formID']
		#print(formID)
		return redirect(url_for('select',formID = formID))

	return render_template(
		'home.html',
		title="Retrieving and Visualizing Your Google Forms Responses",
		)

@app.route("/select/<formID>", methods=["GET", "POST"])
def select(formID):
	if request.method == 'GET':
		return render_template(
				'select.html',
				title="Retrieving and Visualizing Your Google Forms Responses"
				)

	return redirect(url_for('result',formID = formID))


@app.route("/result/<formID>", methods=["GET", "POST"])
def result(formID):
	#print(formID)
	httplib2.debuglevel = 4

	if formID is None:
		return 'Error'
	#if request.method == 'POST':
		#formID = request.form['formID']

	if clientCache.exists(form_id = formID):
		myclient = clientCache.get(form_id = formID)
	else:
		myclient = GoogleFormsApiClient(form_id = formID)
		clientCache.add(form_id = formID, client = myclient)
		
	if formCache.exists(form_id = formID):
		database = formCache.get(form_id = formID)
		double_database = doubleCache.get(form_id = formID)
		message = str(database.numRes) + " responses retrieved from cached data. "
		responses = myclient.get_forms_responses(form_id=formID, 
				timestamp="timestamp > " + database.lastTime)
			
		numNew = database.new_responses(responses)
		numNew = double_database.new_responses(responses)

		if numNew > 0:
			formCache.add(form_id = formID, form = database)
			doubleCache.add(form_id = formID, form = double_database)
			message = message + str(numNew) + " responses retrieved from Google Forms API."

	else:
		forms = myclient.get_forms_questions(form_id = formID)
		responses = myclient.get_forms_responses(form_id=formID, timestamp=None)
		#print(forms)
		#print(responses)

		database = FormDatabase(form_id=formID, 
				forms=forms, 
				responses=responses
				)
			#print(get_json(database))

		double_database = DoubleQDatabase(form_id=formID, 
				forms=forms, 
				responses=responses
				)

		formCache.add(form_id = formID, form = database)
		doubleCache.add(form_id = formID, form = double_database)
		message = str(database.numRes)+" responses retrieved from Google Forms API."

			#watcher = GoogleFormsWatcher(form_id = formID)

	result = database.get_result()
	result_double = double_database.get_result()

	#print(get_json(result_double))
	#print(get_json(database))
	newest = datetime.strptime(database.lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
	        
	return render_template(
		'result.html',
		title="Retrieving and Visualizing Your Google Forms Responses",
		message = message,
		newest = newest.strftime("%Y-%m-%d %I:%M %p"),
		formID=formID,
		data=result,
		data_double=result_double
		)

	return 'Error'


if __name__ == "__main__":
	app.run()