import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
from flask import Flask, jsonify, request, render_template

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():

    return render_template("index.html")

@app.route("/api/v2.0/precipitation")
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

@app.route("/api/v2.0/stations")
def stations():
    session = Session(bind=engine)

    stations = session.query(Station.station).all()

    session.close()

    stations_list = [r[0] for r in stations]

    return jsonify(stations_list)

@app.route("/api/v2.0/form")
def tempForm():

     return render_template("temperature_form.html")

@app.route("/api/v2.0/tobs", methods=["POST", "GET"])
def temperature():
    if request.method == "POST":
        session = Session(engine)

        station = request.form.get('station','USC00511918')

        last_day = max(session.query(Measurement.date).filter(Measurement.station == station).all())[0]
        last_day = dt.datetime.strptime(last_day, "%Y-%m-%d")

        last_year = last_day - dt.timedelta(days=365)

        temps = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == station).\
            filter(Measurement.date >= last_year.strftime('%Y-%m-%d')).\
            order_by(Measurement.date).all()
        session.close()

        return jsonify(temps)

@app.route("/api/v2.0/temp", methods=['POST', 'GET'])
def weather_report():

    if request.method == 'POST':
        session = Session(engine)

        start = request.form.get('testDate', '2016-02-02')

        (TMIN, TAVG, TMAX) = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).first()

        session.close()

        temp_avgs = [TMIN, TAVG, TMAX]

        return jsonify(temp_avgs)

@app.route("/api/v2.0/temps", methods=['POST', 'GET'])
def btn_weather_report():

    if request.method == 'POST':
        session = Session(engine)

        start = request.form.get('startDate', '2017-03-03')
        end = request.form.get('endDate', '2017-03-04')

        (TMIN, TAVG, TMAX) = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).first()
        
        session.close()

        temp_avgs = [TMIN, TAVG, TMAX]

        return jsonify(temp_avgs)


if __name__ == '__main__':
    app.run(debug=True)