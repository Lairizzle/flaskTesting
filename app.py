from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Game state initialization
game_state = {
    'player1_health': 100,
    'player2_health': 100,
    'turn': 1,  # Player 1 starts
    'message': "Player 1's turn to attack!",
    'player1_connected': False,
    'player2_connected': False
}

# Handle a new player joining
@socketio.on('connect')
def on_connect():
    # Check if both players are connected
    if not game_state['player1_connected']:
        game_state['player1_connected'] = True
        emit('game_update', game_state, broadcast=False)
        emit('message', "Player 1 has connected. Waiting for Player 2...", broadcast=True)
    elif not game_state['player2_connected']:
        game_state['player2_connected'] = True
        emit('game_update', game_state, broadcast=False)
        emit('message', "Player 2 has connected. Game starting!", broadcast=True)
        emit('game_update', game_state, broadcast=True)  # Notify both players about the game state
    else:
        emit('message', "Both players are already connected.", broadcast=False)

# Attack logic
def attack(player):
    damage = random.randint(5, 15)  # Random damage for variety
    if player == 1:
        game_state['player2_health'] -= damage
    else:
        game_state['player1_health'] -= damage
    game_state['player2_health'] = max(0, game_state['player2_health'])
    game_state['player1_health'] = max(0, game_state['player1_health'])

# Handle attack event
@socketio.on('attack')
def on_attack():
    player = game_state['turn']
    
    if (player == 1 and game_state['player1_connected']) or (player == 2 and game_state['player2_connected']):
        attack(player)

        # Switch turns
        game_state['turn'] = 2 if player == 1 else 1
        game_state['message'] = f"Player {game_state['turn']}'s turn to attack!"
        
        # Check if someone has won
        if game_state['player1_health'] == 0 or game_state['player2_health'] == 0:
            winner = "Player 1" if game_state['player2_health'] == 0 else "Player 2"
            game_state['message'] = f"{winner} wins!"
            game_state['turn'] = 0  # No more turns after game over
        
        emit('game_update', game_state, broadcast=True)
    else:
        emit('message', "It's not your turn yet!", broadcast=False)

@app.route('/')
def index():
    return render_template('index.html', game_state=game_state)

if __name__ == '__main__':
    socketio.run(app, debug=True)
