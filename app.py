from flask import Flask, render_template, jsonify, make_response, request
from weather import *
import dash_app

flask_app = Flask(__name__)

# Web interface logic
@flask_app.route('/')
def main_page():
    return render_template('main.html')


@flask_app.route('/favicon.ico')
def favicon():
    return '', 204


@flask_app.route('/get_weather_data', methods=['POST'])
def get_weather_data():
    latitude = float(request.form['latitude'])
    longitude = float(request.form['longitude'])

    location_key = get_location_by_geoposition(latitude, longitude)['location_key']
    weather_data = get_current_weather(location_key)
    if weather_data is None:
        return jsonify({})

    for data in weather_data:
        data["weather_type"] = get_weather_type(float(data["temperature"]),
                                                float(data["humidity"]),
                                                float(data["windSpeed"]),
                                                float(data["precipitationProbability"]))

    dash_app.dash_app1.layout.children[0].data = weather_data

    return jsonify(weather_data)


@flask_app.route('/check_weather_type', methods=['POST'])
def check_weather_type():
    temperature = float(request.form['temperature'])
    humidity = float(request.form['humidity'])
    wind_speed = float(request.form['windSpeed'])
    precipitation = float(request.form['precipitation'])

    weather_type = get_weather_type(temperature, humidity, wind_speed, precipitation)
    return jsonify({'weather_type': weather_type})


@flask_app.route('/get_weather_in_points', methods=['POST'])
def get_weather_in_points():
    points = []
    print(request.form)

    if bool(request.form['city'] == 'true'):
        points.append(get_location_by_city(request.form['city-1']))
        points.append(get_location_by_city(request.form['city-2']))

        stop_index = 1
        while f'city-stop-{stop_index}' in request.form:
            stop = get_location_by_city(request.form[f'city-stop-{stop_index}'])
            points.insert(-1, stop)
            stop_index += 1
    else:
        points.append(get_location_by_geoposition(float(request.form['latitude-1']), float(request.form['longitude-1'])))
        points.append(get_location_by_geoposition(float(request.form['latitude-2']), float(request.form['longitude-2'])))

        stop_index = 1
        while f'latitude-stop-{stop_index}' in request.form and f'longitude-stop-{stop_index}' in request.form:
            stop = get_location_by_geoposition(
                float(request.form[f'latitude-stop-{stop_index}']),
                float(request.form[f'longitude-stop-{stop_index}'])
            )
            points.insert(-1, stop)
            stop_index += 1

    weather_data = []
    for point in points:
        if isinstance(point, dict):
            city_name = point.get("city_name", f"{point.get('latitude', 'unknown')}, {point.get('longitude', 'unknown')}")
        else:
            city_name = str(point)  # Если точка — строка (например, название города)

        forecast = get_current_weather(point["location_key"], request.form['forecast-time'])
        if forecast is None:
            continue

        for weather in forecast:
            weather["weather_type"] = get_weather_type(
                float(weather["temperature"]),
                float(weather["humidity"]),
                float(weather["windSpeed"]),
                float(weather["precipitationProbability"])
            )
            weather["city"] = city_name

        weather_data.append(forecast)

    dash_app.dash_app3.layout.children[0].data = weather_data
    dash_app.dash_app3.layout.children[1].data = {'unit': 'hours', 'value': 12} if request.form['forecast-time'] == '12_hours' else {'unit': 'days', 'value': 5}

    return jsonify(weather_data)


@flask_app.errorhandler(404)
def not_found(error):
    if error is None:
        error = "Object not found"
    return make_response(jsonify({'error': error}), 404)


@flask_app.errorhandler(400)
def bad_request(error):
    if error is None:
        error = "Invalid request"
    return make_response(jsonify({'error': error}), 400)


dash_app.initialize_dash(flask_app)

if __name__ == '__main__':
    flask_app.run()

