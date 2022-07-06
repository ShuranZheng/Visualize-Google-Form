from flask import Flask, request, redirect
from flask import current_app as app
from flask import render_template

from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools

from GFClient import GoogleFormsApiClient
from database import FormDatabase

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
	if request.method == 'POST':
		return redirect("/result", code = 307)

	return render_template(
		'home.html',
		title="Retrieving and Visualizing Your Google Forms Responses",
		)


@app.route("/result", methods=["POST"])
def home_post():
	formID = request.form['formID']
	myclient = GoogleFormsApiClient()
	forms = myclient.get_forms_questions(form_id = formID)
	responses = myclient.get_forms_responses(form_id=formID)

	database = FormDatabase(form_id=formID, forms=forms, responses=responses)
	result = database.get_result()
        

	return render_template(
		'home_post.html',
		title="Retrieving and Visualizing Your Google Forms Responses",
		formID=formID,
		data=result
		)


if __name__ == "__main__":
	app.run()