from flask import Flask, request, jsonify
from datetime import datetime
import uuid


app = Flask(__name__)

events = {}  # In-memory storage for events


def parse_datetime(date_time_str, format='%Y-%m-%dT%H:%M:%S'):
    try:
        return datetime.strptime(date_time_str, format)
    except ValueError:
        raise ValueError('Invalid datetime format')


def validate_event_data(data):
    required_fields = {'description', 'time'}
    return all(field in data for field in required_fields)


def create_event():
    data = request.get_json()
    if not validate_event_data(data):
        return jsonify({'error': 'Invalid request body'}), 400

    try:
        event_time = parse_datetime(data['time'])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    event_id = str(uuid.uuid4())
    event = {'id': event_id, 'description': data['description'], 'time': event_time}
    events[event_id] = event
    return jsonify(event), 201


def get_event(event_id):
    event = events.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(event)


def get_events():
    datetime_format = request.args.get('datetime_format', '%Y-%m-%dT%H:%M:%S')
    from_time_str = request.args.get('from_time')
    to_time_str = request.args.get('to_time')

    try:
        from_time = parse_datetime(from_time_str, datetime_format) if from_time_str else datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)
        to_time = parse_datetime(to_time_str, datetime_format) if to_time_str else datetime.now()
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    matching_events = [
        event for event_id, event in events.items()
        if from_time <= event['time'] <= to_time
    ]

    for event in matching_events:
        if isinstance(event['time'], str):
            event['time'] = event['time'].strftime(datetime_format)
        else:
            pass

    return jsonify(matching_events)



app.route('/events', methods=['POST'])(create_event)
app.route('/events/<event_id>', methods=['GET'])(get_event)
app.route('/events', methods=['GET'])(get_events)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    #app.run()