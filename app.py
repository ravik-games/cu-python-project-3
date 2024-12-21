from flask import Flask, render_template, jsonify, make_response, request
from weather import *

app = Flask(__name__)

# Web interface logic
@app.route('/')
def main_page():
    return render_template('main.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/get_weather_data', methods=['POST'])
def get_weather_data():
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    location_key = get_location_by_geoposition(latitude, longitude)
    weather_data = get_current_weather(location_key)
    if weather_data is None:
        return jsonify({})

    weather_data["weather_type"] = get_weather_type(float(weather_data["temperature"]),
                                                    float(weather_data["humidity"]),
                                                    float(weather_data["windSpeed"]),
                                                    float(weather_data["precipitationProbability"]))
    return jsonify(weather_data)


@app.route('/check_weather_type', methods=['POST'])
def check_weather_type():
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    wind_speed = float(request.form['windSpeed'])
    precipitation = float(request.form['precipitation'])

    weather_type = get_weather_type(temperature, humidity, wind_speed, precipitation)
    return jsonify({'weather_type': weather_type})


@app.route('/get_weather_in_points', methods=['POST'])
def get_weather_in_points():
    if bool(request.form['city']):
        first_point = get_location_by_city(request.form['city-1'])
        second_point = get_location_by_city(request.form['city-2'])
    else:
        first_point = get_location_by_geoposition(float(request.form['latitude-1']), float(request.form['longitude-1']))
        second_point = get_location_by_geoposition(float(request.form['latitude-2']), float(request.form['longitude-2']))

    first_weather = get_current_weather(first_point)
    second_weather = get_current_weather(second_point)

    if first_weather is None or second_weather is None:
        return jsonify({})

    first_weather["weather_type"] = get_weather_type(float(first_weather["temperature"]),
                                                    float(first_weather["humidity"]),
                                                    float(first_weather["windSpeed"]),
                                                    float(first_weather["precipitationProbability"]))

    second_weather["weather_type"] = get_weather_type(float(second_weather["temperature"]),
                                                     float(second_weather["humidity"]),
                                                     float(second_weather["windSpeed"]),
                                                     float(second_weather["precipitationProbability"]))

    return jsonify([first_weather, second_weather])


@app.errorhandler(404)
def not_found(error):
    if error is None:
        error = "Object not found"
    return make_response(jsonify({'error': error}), 404)


@app.errorhandler(400)
def bad_request(error):
    if error is None:
        error = "Invalid request"
    return make_response(jsonify({'error': error}), 400)


if __name__ == '__main__':
    app.run()
