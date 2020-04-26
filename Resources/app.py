import os
import sqlite3
import pandas as pd

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import json
from flask import Flask, jsonify
from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii_3.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to tables(Measurement/Station)
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)



#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

#################################################
# Flask Routes
#################################################

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"<b>Surf's Up Homepage!</b><br/>"
        f"<i>Available Routes:</i><br/>"
        f"<p> <b>Precipitation:</b><br/>" 
        f"<p>   * /api/v1.0/precipitation<br/>"
        f"<p> <b>Station List: </b><br/>"
        f"<p>   * /api/v1.0/stations<br/>"
        f"<p> <b>Most Active Station (Temperatures): </b><br/>"
        f"<p>   * /api/v1.0/tobs<br/>"
        f"<p> <b>JSON list given only 'Start Date'(YYYY-MM-DD): </b><br/>"
        f"<p>   * /api/v1.0/<start><br/>"
        f"<p> <b>JSON list given 'Start Date'(YYYY-MM-DD) /'End Date'(YYYY-MM-DD): </b><br/>"
        f"<p>   * /api/v1.0/<start_date>/<end_date><br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    twelve_months = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date > '2016-08-23').\
    order_by(measurement.date.desc()).all()

    precipitation= []
    for result in twelve_months:
        row = {"date":"prcp"}
        row["date"] = result[0]
        row["prcp"] = result[1]
        precipitation.append(row)
    #Rain = list(np.ravel(twelve_months))

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    #stations = session.query(measurement).filter(measurement.station)
   st = session.query(station.station, station.name).limit(10).all()
   #station = list(np.ravel(st))

   stationx= []
   for x in st:
       row2 = {'station': 'name'}
       row2['station'] = x[0]
       row2['name'] = x[1]
       stationx.append(row2)

   return jsonify(stationx)

@app.route("/api/v1.0/tobs")
#* Query the dates and temperature observations of the most active station for the last year of data.
def tobs():
    something = session.query(measurement.date, measurement.tobs).filter(measurement.date > '2016-08-23').\
            filter(measurement.station == "USC00519281").all()
    #most_active_temp = list(np.ravel(something))
    
    tobs_temp = []
    for s in something: 
        row3 = {'Date':'Temperature'}
        row3['Date'] = s[0]
        row3['Tobs'] = s[1]
        tobs_temp.append(row3)
    return jsonify(tobs_temp)

#* When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start_date>")
def calc_temps(start_date= 'start_date'):
    start_temp_date = session.query(measurement.date,func.max(measurement.tobs), \
        func.min(measurement.tobs),\
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).group_by(measurement.date).all()
    start_date_list = []
    for a in start_temp_date:
        stl_d = {}
        stl_d["Date"] = a[0]
        stl_d["Max"] = a[1]
        stl_d["Min"] = a[2]
        stl_d["Avg"] = a[3]
        start_date_list.append(stl_d)

    return jsonify(start_date_list)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_2(start_date= 'start_date', end_date='end_date'):
    start_end = session.query(measurement.date,func.max(measurement.tobs), \
        func.min(measurement.tobs),\
        func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date, measurement.date <= end_date).group_by(measurement.date).all()
    vacation_list = []
    for y in start_end:
        se = {}
        se["Date"] = y[0]
        se["Max"] = y[1]
        se["Min"] = y[2]
        se["Avg"] = y[3]
        vacation_list.append(se)
    return jsonify(vacation_list)
if __name__ == '__main__':
    app.run(debug=True)

# * When given start-end, calculate the `TMIN`, `TAVG`, and `TMAX` for dates btwn start and end inclusive.
#* Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
# for a given start or start-end range.