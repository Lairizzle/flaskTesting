from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

# Store game rooms with passwords
rooms = {}

# Homepage (game room list)
@app.route('/')
def home():
    return render_template('index.html', rooms=rooms)

# Room creation route
@app.route('/create_room', methods=['POST'])
def create_room():
    room_name = request.form['room_name']
    password = request.form['password']
    if room_name in rooms:
        return jsonify({'error': 'Room already exists!'}), 400
    rooms[room_name] = {'password': password, 'players': []}
    return redirect(url_for('game_room', room_name=room_name))

# Room joining route
@app.route('/join_room', methods=['POST'])
def join_room_route():
    room_name = request.form['room_name']
    password = request.form['password']
    if room_name not in rooms:
        return jsonify({'error': 'Room does not exist!'}), 404
    if rooms[room_name]['password'] != password:
        return jsonify({'error': 'Incorrect password!'}), 403
    return redirect(url_for('game_room', room_name=room_name))

# Game room route (players join here)
@app.route('/room/<room_name>', methods=['GET'])
def game_room(room_name):
    if room_name not in rooms:
        return redirect(url_for('home'))
    return render_template('game_room.html', room_name=room_name)

# SocketIO events
@socketio.on('join')
def handle_join(data):
    room_name = data['room_name']
    username = data['username']
    join_room(room_name)
    rooms[room_name]['players'].append(username)
    send(f'{username} has joined the room.', room=room_name)

@socketio.on('message')
def handle_message(data):
    room_name = data['room_name']
    message = data['message']
    send(message, room=room_name)

@socketio.on('leave')
def handle_leave(data):
    room_name = data['room_name']
    username = data['username']
    leave_room(room_name)
    rooms[room_name]['players'].remove(username)
    send(f'{username} has left the room.', room=room_name)

if __name__ == '__main__':
    socketio.run(app, debug=True)
