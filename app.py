import os, json, threading
from flask import Flask, jsonify, request

app = Flask(__name__)
lock = threading.Lock()
CODES_FILE = 'codes.json'
API_KEY = os.environ.get('CODE_LOCKER_API_KEY')  # For security when deployed

# Function to load codes from the JSON file
def load_codes():
    if os.path.exists(CODES_FILE):
        with open(CODES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Function to save codes back to the JSON file
def save_codes(codes):
    tmp = CODES_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CODES_FILE)

# A simple homepage to confirm the server is running
@app.route('/')
def home():
    return "Code Locker API running."

# URL to get a specific code snippet by its name
# Example: /get_code/GP1
@app.route('/get_code/<name>', methods=['GET'])
def get_code(name):
    codes = load_codes()
    c = codes.get(name)
    if c is None:
        return jsonify({"error":"Code not found"}), 404
    return jsonify({"code": c})

# URL to list the names of all saved snippets
@app.route('/list_codes', methods=['GET'])
def list_codes():
    return jsonify({"names": list(load_codes().keys())})

# URL to add a new code snippet
@app.route('/add_code', methods=['POST'])
def add_code():
    # Optional security check for an API key
    key = request.headers.get('X-API-KEY')
    if API_KEY and key != API_KEY:
        return jsonify({"error":"unauthorized"}), 401

    data = request.get_json() or {}
    name = data.get('name')
    code = data.get('code')
    if not name or not code:
        return jsonify({"error":"must provide name and code"}), 400

    with lock:
        codes = load_codes()
        codes[name] = code
        save_codes(codes)
    return jsonify({"ok": True, "name": name})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)