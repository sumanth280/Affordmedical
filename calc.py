from flask import Flask, jsonify, request
import requests
import threading
app = Flask(_name_)
WINDOW_SIZE = 10
THIRD_PARTY_API = 'http://20.244.56.144/test/auth/{numberid}' 
LOCK = threading.Lock()
window = []
def fetch_number(number_id):
    url = THIRD_PARTY_API.format(number_id)
    try:
        response = requests.get(url, timeout=0.5)
        response.raise_for_status()
        number = response.json().get('number')
        return number
    except (requests.RequestException, ValueError, KeyError):
        return None
@app.route('/numbers/<string:number_id>', methods=['POST'])
def get_numbers(number_id):
    if number_id not in ['p', 'f', 'e', 'r']:
        return jsonify({'error': 'Invalid number ID'}), 400
    number = fetch_number(number_id)
    if number is None:
        return jsonify({'error': 'Failed to fetch number'}), 500
    with LOCK:
        window_prev_state = list(window)
        if number not in window:
            if len(window) >= WINDOW_SIZE:
                window.pop(0)
            window.append(number)
        window_curr_state = list(window)
        avg = sum(window) / len(window) if window else 0.0
    return jsonify({
        'windowPrevState': window_prev_state,
        'windowCurrState': window_curr_state,
        'numbers': [number],
        'avg': round(avg, 2)
    })
if _name_ == '_main_':
    app.run(port=9876, debug=True)