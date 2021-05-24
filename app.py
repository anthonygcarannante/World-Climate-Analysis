from flask import Flask
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

# Database Setup
database_path = "/Users/anthonycarannante/Desktop/UPennDBC_WorkingFolder/Homework_Submissions/SQLAlchemy-challenge/Assignment/Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the table
measurements = Base.classes.measurement
stations = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print("Server...")
    precip = "/api/v1.0/precipitation"
    stations = "/api/v1.0/stations"
    tobs = "/api/v1.0/tobs"
    start = "/api/v1.0/start"
    start_end = "/api/v1.0/start/end"

    return (f"Precipiation Route: {precip}<br/>"
        f"Station Route: {stations}<br/>"
        f"Temperature Data: {tobs}<br/>"
        f"Start: {start}<br/>"
        f"Start/End: {start_end}<br/>")

@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to the DB
    session = Session(engine)

    # Return the latest 12 months of precipitation data
    latest_date = session.query(measurements.date).order_by(measurements.date.desc()).first()
    latest_date = dt.date(2017,8,23)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(measurements.date, measurements.prcp).\
    filter(measurements.date >= year_ago).\
    order_by(measurements.date.desc()).all()

    # Close Session
    session.close()

    # Place data into dictionary in format {"date string": precipitation float}
    all_prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp_data.append(prcp_dict)
    
    # Return JSONified list of dictionaries
    return jsonify(all_prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to the DB
    session = Session(engine)
    
    # Query number of stations
    stations_data = session.query(measurements.station).distinct().all()

    # Close Session
    session.close()

    # Transform the data into a structure than can be jsonified
    stations_list = list(np.ravel(stations_data))

    # Return number of stations
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)

    # Pull temperature observations from the last year at Station USC00519281
    latest_date = dt.date(2017,8,23)
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    station_temp_data = session.query(measurements.tobs).\
                        filter(measurements.date >= year_ago).\
                        filter(measurements.station == 'USC00519281').\
                        order_by(measurements.date.desc()).all()

    # Close Session
    session.close()

    # Transform the data into a structure than can be jsonified
    station_temp_list = list(np.ravel(station_temp_data))

    return jsonify(station_temp_list)

@app.route("/api/v1.0/start")
def start():

        # Create session from Python to the DB
    session = Session(engine)
    
    station_frequency = session.query(measurements.station, func.count(measurements.station)).\
    group_by(measurements.station).\
    order_by(func.count(measurements.station).desc()).all()
    station_frequency_df = pd.DataFrame(station_frequency,columns=['Station','Frequency'])

    most_frequent_station = station_frequency_df['Station'][0]
    start_date =  dt.date(2014,8,23)

    Tmin = session.query(func.min(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.station == most_frequent_station).all()[0]

    Tmax = session.query(func.max(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.station == most_frequent_station).all()[0]
                    
    Tavg = session.query(func.avg(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.station == most_frequent_station).all()[0]

    # Close Session
    session.close()

    temps_list = list(np.ravel([Tmin,Tmax,Tavg]))
    return jsonify(temps_list)
    return

@app.route("/api/v1.0/start/end")
def start_end():
    # Create session from Python to the DB
    session = Session(engine)
    
    station_frequency = session.query(measurements.station, func.count(measurements.station)).\
    group_by(measurements.station).\
    order_by(func.count(measurements.station).desc()).all()
    station_frequency_df = pd.DataFrame(station_frequency,columns=['Station','Frequency'])

    most_frequent_station = station_frequency_df['Station'][0]
    start_date =  dt.date(2016,8,23)
    end_date = dt.date(2017,8,23)

    Tmin = session.query(func.min(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.date <= end_date).\
                    filter(measurements.station == most_frequent_station).all()[0]

    Tmax = session.query(func.max(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.date <= end_date).\
                    filter(measurements.station == most_frequent_station).all()[0]
                    
    Tavg = session.query(func.avg(measurements.tobs)).\
                    filter(measurements.date >= start_date).\
                    filter(measurements.date <= end_date).\
                    filter(measurements.station == most_frequent_station).all()[0]

    # Close Session
    session.close()

    temps_list = list(np.ravel([Tmin,Tmax,Tavg]))
    return jsonify(temps_list)

if __name__ == "__main__":
    app.run(debug=True)
