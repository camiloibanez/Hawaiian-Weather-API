import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (f"Hawaii Weather Report Data<br/>"
            f"available routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/yyyy-mm-dd<br/>"
            f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(bind=engine)

    precip = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    rain_records = []

    for (date, precipitation) in precip:
        record_dict = {}
        record_dict['date'] = date
        record_dict['rain'] = precipitation
        rain_records.append(record_dict)
    
    return jsonify(rain_records)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(bind=engine)

    stations = session.query(Station.station).all()

    session.close()

    stations_list = [r[0] for r in stations]

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperature():
    session = Session(engine)

    last_day = dt.datetime.strptime(max(session.query(Measurement.date).all())[0], "%Y-%m-%d")
    
    last_year = last_day - dt.timedelta(days=365)

    temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                                    filter(Measurement.date >= last_year.strftime('%Y-%m-%d')).\
                                    order_by(Measurement.date).all()
    session.close()

    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def weather_report(start):
    session = Session(engine)

    (TMIN, TAVG, TMAX) = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                    filter(Measurement.date >= start).first()

    session.close()

    temp_avgs = [TMIN, TAVG, TMAX]

    return jsonify(temp_avgs)

@app.route("/api/v1.0/<start>/<end>")
def btn_weather_report(start, end):
    session = Session(engine)

    (TMIN, TAVG, TMAX) = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                    filter(Measurement.date >= start).\
                                    filter(Measurement.date <= end).first()
    
    session.close()

    temp_avgs = [TMIN, TAVG, TMAX]

    return jsonify(temp_avgs)


if __name__ == '__main__':
    app.run(debug=True)