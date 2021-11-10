#Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set up the database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a variable for each of the classes so that we can refer later
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session link from Python to our datavse
session = Session(engine)

# Set up flask
# All of your routes should go after the app = Flask(__name__) line of code
app = Flask(__name__)

# Create Welcome route
@app.route("/")
def welcome():
    return(
     '''
    Welcome to the Climate Analysis API!\n
    Available Routes:\n
    /api/v1.0/precipitation\n
    /api/v1.0/stations\n
    /api/v1.0/tobs\n
    /api/v1.0/temp/start/end
     '''
    )

# Create Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago fromthe most recent date in the databse
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Get the date and percipitation for the prev year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    
    # Loop through to get the key:value pair date:precipitation
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
    
# Create Station route
@app.route("/api/v1.0/stations")
def stations():
    # Create query to get all of the stations in database
    results = session.query(Station.station).all()

    # Unravel results into a 1dimensional array then convert it into a list. Then jsonify the list
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

# Create Monthly Temp route
@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date one year agp from the last date in the databse
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all the temperature observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    # unravel list into 1 dimensional array and convert into a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

# Statistics Route for temp
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Create query to select the min, max, and max temp 
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Determine the start and end date 
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    # Calculate the emp min, avg, max with start and end dates
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run()