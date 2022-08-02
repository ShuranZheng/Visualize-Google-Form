from flask import Flask, request, redirect
from flask import current_app as app
from flask import render_template

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from typing import List, Dict
from datetime import datetime

from GFClient import GoogleFormsApiClient
from GFWatcher import GoogleFormsWatcher
from database import FormDatabase
from cache import FormCache, ClientCache
import json
import logging
import httplib2

httplib2.debuglevel = 4

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formCache = FormCache()
clientCache = ClientCache()

def get_json(obj):
  return json.loads(
    json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
  )

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == 'POST':
		return redirect("/result", code = 307)

	return render_template(
		'home.html',
		title="Retrieving and Visualizing Your Google Forms Responses",
		)


@app.route("/result", methods=["GET", "POST"])
def home_post():
	if request.method == 'POST':
		formID = request.form['formID']

		if clientCache.exists(form_id = formID):
			myclient = clientCache.get(form_id = formID)
		else:
			myclient = GoogleFormsApiClient(form_id = formID)
			clientCache.add(form_id = formID, client = myclient)
		
		if formCache.exists(form_id = formID):
			database = formCache.get(form_id = formID)
			message = str(database.numRes) + " responses retrieved from cached data. "
			responses = myclient.get_forms_responses(form_id=formID, 
					timestamp="timestamp > " + database.lastTime)
			
			numNew = database.new_responses(responses)
			if numNew > 0:
				formCache.add(form_id = formID, form = database)
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

			formCache.add(form_id = formID, form = database)
			message = str(database.numRes)+" responses retrieved from Google Forms API."

			#watcher = GoogleFormsWatcher(form_id = formID)

		result = database.get_result()
		#print(get_json(database))
		newest = datetime.strptime(database.lastTime, "%Y-%m-%dT%H:%M:%S.%fZ")
	        
		return render_template(
			'home_post.html',
			title="Retrieving and Visualizing Your Google Forms Responses",
			message = message,
			newest = newest.strftime("%Y-%m-%d %I:%M %p"),
			formID=formID,
			data=result
			)

	return 'Error'


if __name__ == "__main__":
	app.run()