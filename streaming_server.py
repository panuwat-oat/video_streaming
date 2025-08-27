from flask import Flask, jsonify, send_file, request, abort
from flask_cors import CORS
import jwt
import time

app = Flask(__name__)
CORS(app)

SECRET_KEY = 'demo-secret-key'

# อ่าน HLS key
with open('hls_key.bin', 'rb') as f:
    HLS_KEY = f.read()

USERS = {'demo': 'demo123'}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username] == password:
        token = jwt.encode({
            'user_id': username,
            'exp': time.time() + 3600
        }, SECRET_KEY, algorithm='HS256')
        return jsonify({'success': True, 'token': token})
    
    return jsonify({'success': False}), 401

@app.route('/playlist')
def get_playlist():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        abort(401)
    
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return send_file('encrypted_hls.m3u8', mimetype='application/vnd.apple.mpegurl')
    except:
        abort(401)

@app.route('/hlskey')
def get_hls_key():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        abort(401)
    
    try:
        jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print("HLS Key requested by authenticated user")
        return send_file('hls_key.bin')
    except:
        abort(401)

@app.route('/<path:filename>')
def serve_segments(filename):
    if filename.endswith('.ts'):
        return send_file(filename)
    abort(404)

if __name__ == '__main__':
    app.run(port=8001, debug=True)
