from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
import os
from tempfile import mkdtemp
import datetime
from datetime import datetime, timezone
import time
import calendar
import helpers

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test")
def test():
        return render_template("test.html")

@app.route("/Gramps")
def Gramps():

    # Get current variable information
    today = datetime.now(timezone.utc).strftime("%m/%d/%Y")
    q = datetime.now(timezone.utc).strftime("%Y")
    j = int(q) - 1
    stn = '045'
    stn2 = '201'
    startdate = datetime.now(timezone.utc).strftime(f"%m/%d/{j}") # MM/DD/YYYY
    enddate = today

    # Run the get ocean temperature modules from helpers.py. Returns the current ocean temp and past ocean temp converted to F
    results = helpers.ocean_data(stn, startdate, enddate)
    results_secondary = helpers.ocean_data(stn2, startdate, enddate)
    airData = helpers.air_data()
    surflineData = helpers.surfline_data()

    # Round the two temperatures to get an appoximate temp for ponto north
    temp1 = round((results[0] + results_secondary[0]) / 2, 2)
    temp2 = round((results[1] + results_secondary[1]) / 2, 2)

    # Round the two wave heights to get an approximate wave ht for ponto north
    waveHt = round((results[2] + results_secondary[2]) / 2, 2)

    # Pass parameters to prediction algorithm
    myPrediction = helpers.prediction(airData[1], waveHt, results[4], surflineData[0])

    return render_template("gramps.html", temp1=temp1, temp2=temp2, airTemp=airData[0], windSpeed=airData[1], windDir=airData[2], waveHt=waveHt, waveTime=results[3], waveDir=results[4], tide=surflineData[0], surflinePrediction=surflineData[1], myPrediction=myPrediction)