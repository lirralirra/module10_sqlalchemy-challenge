# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year."""
    session = Session(engine)  # Create a new session to interact with the database

    last_date = session.query(func.max(Measurement.date)).scalar()  # Get the last date in the dataset
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)  # Calculate one year ago

    # Query for precipitation data from one year ago to the last date
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()  # Close the session after completing the query

    all_precipitation = {date: prcp for date, prcp in results}  # Create a dictionary of date and precipitation values
    return jsonify(all_precipitation)  # Return JSON response


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    session = Session(engine)  # Create a new session to interact with the database

    results = session.query(Station.station).all()  # Query all station IDs

    session.close()  # Close the session after completing the query

    all_stations = list(np.ravel(results))  # Flatten results into a list
    return jsonify(all_stations)  # Return JSON response


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return temperature observations (tobs) for previous year from most active station."""
    session = Session(engine)  # Create a new session to interact with the database

    last_date = session.query(func.max(Measurement.date)).scalar()  # Get the last date in the dataset
    one_year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)  # Calculate one year ago

    most_active_station_id = 'USC00519281'  # Specify most active station ID directly

    # Query temperature observations from the most active station over the past year
    results = session.query(Measurement.tobs). \
        filter(Measurement.station == most_active_station_id). \
        filter(Measurement.date >= one_year_ago).all()

    session.close()  # Close the session after completing the query

    temps = list(np.ravel(results))  # Flatten results into a list

    return jsonify(temps)  # Return JSON response


@app.route("/api/v1.0/<start>")
def start_route(start):
    """Return min, avg, and max temperatures from start date to end of dataset."""
    session = Session(engine)  # Create a new session to interact with the database

    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()  # Query for min, avg, and max temperatures from start date onward

    session.close()  # Close the session after completing the query

    temps = list(np.ravel(results))  # Flatten results into a list
    return jsonify({
        "TMIN": temps[0],
        "TAVG": temps[1],
        "TMAX": temps[2]
    })  # Return JSON response


@app.route("/api/v1.0/<start>/<end>")
def start_end_route(start, end):
    """Return min, avg, and max temperatures from start date to end date."""
    session = Session(engine)  # Create a new session to interact with the database

    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(
        Measurement.date <= end).all()  # Query for min, avg, and max temperatures between start and end dates

    session.close()  # Close the session after completing the query

    temps = list(np.ravel(results))  # Flatten results into a list
    return jsonify({
        "TMIN": temps[0],
        "TAVG": temps[1],
        "TMAX": temps[2]
    })  # Return JSON response


if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode