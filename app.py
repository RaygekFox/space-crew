from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import time
import threading
import random
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store connected clients count
connected_clients = 0

# Game state
game_running = True
tick_counter = 0
counted_ticks = 0  # New counter that can be paused
counting_enabled = True  # Flag to control if counted_ticks should be incremented
last_tick_time = 0
game_loop_started = False
game_over = False
dt = 1  # Time between ticks (in game units)

# Difficulty settings
difficulty_settings = {
    'temperature': False,  # If False, temperature values stay constant
    'electricity': False,  # If False, battery levels stay constant
    'connection': False    # If False, connection levels stay constant
}

# Initial temperature and other values that we'll store if difficulty is set to easy
initial_values = {
    't': 0,       # Hull temperature
    't_l': 0,     # Left engine temperature
    't_r': 0,     # Right engine temperature
    't_c': 0,     # Battery temperature
    'c': 1000,    # Battery charge
    'ls': 1       # Connection level
}

# Game parameters as specified in the instructions
game_state = {
    'h': 0,             # Висота ракети над рівнем моря
    'p': 1,             # Тиск атмосфери
    'v_y': 0,           # Вертикальна швидкість
    'v_x': 0,           # Горизонтальна швидкість
    'alpha': 0,         # Кут ракети відносно землі
    'f': 10000,          # Кількість палива в двигуні
    'ns': 5,            # Кількість залишившихся стадій ракети
    'e_l': 0,           # Потужність лівого двигуна
    'e_r': 0,           # Потужність правого двигуна
    't': 0,             # Температура корпусу ракети
    't_l': 0,           # Температиура лівого двигуна
    't_r': 0,           # Температура правого двигуна
    'c': 1000,          # Рівень заряду батареї
    't_c': 0,           # Температура батареї
    'sp': 0,            # Стан сонячних панелей
    'ls': 1,            # Рівень звʼязку
    'mu_in': 100,       # Частота вхідного сигналу
    'mu_r': 100,        # Частота приймача
    'game_over': False, # Game over flag
    'v_y_change': 0,    # Added for frontend
    'a_grav': 0,        # Added for frontend
    'a_orbit': 0        # Added for frontend
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global connected_clients, game_loop_started, tick_counter, counted_ticks, counting_enabled, game_state, difficulty_settings
    
    # Increment connected clients
    connected_clients += 1
    
    # Send current game state to new client
    emit('client_count', {'count': connected_clients}, broadcast=True)
    emit('tick_update', {'ticks': tick_counter, 'counted_ticks': counted_ticks, 'counting_enabled': counting_enabled})
    emit('game_state_update', game_state, broadcast=True)
    emit('difficulty_settings', difficulty_settings)
    
    # Start the game loop only once, when the first client connects
    if not game_loop_started:
        socketio.start_background_task(game_loop)
        game_loop_started = True

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients -= 1
    emit('client_count', {'count': connected_clients}, broadcast=True)

@socketio.on('toggle_counting')
def handle_toggle_counting():
    global counting_enabled
    counting_enabled = not counting_enabled
    emit('counting_toggled', {'counting_enabled': counting_enabled}, broadcast=True)

@socketio.on('reset_game')
def handle_reset_game():
    global game_state, game_over, initial_values
    
    # Reset game variables to initial values
    game_state = {
        'h': 0, 'p': 1, 'v_y': 0, 'v_x': 0, 'alpha': 0, 'f': 10000, 'ns': 5,
        'e_l': 0, 'e_r': 0, 't': 0, 't_l': 0, 't_r': 0, 'c': 1000, 't_c': 0,
        'sp': 0, 'ls': 1, 'mu_in': 100, 'mu_r': 100, 'game_over': False,
        'v_y_change': 0,
        'a_grav': 0,
        'a_orbit': 0
    }
    game_over = False
    
    # Reset the initial values
    initial_values = {
        't': 0,
        't_l': 0,
        't_r': 0,
        't_c': 0,
        'c': 1000,
        'ls': 1
    }
    
    # Broadcast reset to all clients
    emit('game_state_update', game_state, broadcast=True)
    emit('game_reset', broadcast=True)

@socketio.on('update_difficulty')
def handle_update_difficulty(data):
    global difficulty_settings, initial_values, game_state
    
    # Update difficulty settings
    difficulty_settings = {
        'temperature': data.get('temperature', False),
        'electricity': data.get('electricity', False),
        'connection': data.get('connection', False)
    }
    
    # If we're turning on a difficulty that was previously off,
    # we need to save the current values as our new baseline
    if difficulty_settings['temperature']:
        initial_values['t'] = game_state['t']
        initial_values['t_l'] = game_state['t_l']
        initial_values['t_r'] = game_state['t_r']
        initial_values['t_c'] = game_state['t_c']
    
    if difficulty_settings['electricity']:
        initial_values['c'] = game_state['c']
    
    if difficulty_settings['connection']:
        initial_values['ls'] = game_state['ls']
    
    # Broadcast the updated settings to all clients
    emit('difficulty_settings', difficulty_settings, broadcast=True)

@socketio.on('control_action')
def handle_control_action(data):
    global game_state
    
    action = data.get('action')
    
    # Handle different control actions
    if action == 'increase_left_engine' and game_state['e_l'] < 5 and game_state['f'] > 0:
        game_state['e_l'] += 1
    
    elif action == 'decrease_left_engine' and game_state['e_l'] > 0:
        game_state['e_l'] -= 1
    
    elif action == 'increase_right_engine' and game_state['e_r'] < 5 and game_state['f'] > 0:
        game_state['e_r'] += 1
    
    elif action == 'decrease_right_engine' and game_state['e_r'] > 0:
        game_state['e_r'] -= 1
    
    elif action == 'toggle_solar_panels':
        game_state['sp'] = 1 - game_state['sp']  # Toggle between 0 and 1
    
    elif action == 'increase_receiver_freq':
        game_state['mu_r'] += 1
    
    elif action == 'decrease_receiver_freq':
        game_state['mu_r'] -= 1
    
    elif action == 'detach_stage' and game_state['ns'] > 0:
        game_state['ns'] -= 1
        game_state['f'] = 10000  # Refill fuel on stage detach
    
    # Broadcast updated game state to all clients
    emit('game_state_update', game_state, broadcast=True)

def update_game_state():
    """Update game state variables based on the rules"""
    global game_state, game_over, tick_counter, difficulty_settings, initial_values
    
    # Skip updates if game is over
    if game_state['game_over']:
        return
    
    # Store original values before updating
    original_values = {
        't': game_state['t'],
        't_l': game_state['t_l'],
        't_r': game_state['t_r'],
        't_c': game_state['t_c'],
        'c': game_state['c'],
        'ls': game_state['ls']
    }
    
    # Randomly update mu_in (input frequency) with 1% chance per tick
    if random.random() < 0.1:
        game_state['mu_in'] += random.randint(-1, 1)
    
    # Calculate atmospheric pressure based on height
    game_state['p'] = max(0, 1 - game_state['h'] / 100000)
    
    # Update rocket angle
    angle_change = (game_state['e_l'] - game_state['e_r']) * dt
    game_state['alpha'] = (game_state['alpha'] + angle_change) % 360
    
    # Convert angle to radians for calculations
    alpha_rad = math.radians(game_state['alpha'])
    
    # Update velocities
    total_engine_power = game_state['e_l'] + game_state['e_r']
    if game_state['f'] == 0:
        total_engine_power = 0
    
    # Hack: Prevent vertical speed from decreasing when at ground level (h=0)
    a_engine = 5 * total_engine_power * math.cos(alpha_rad)
    a_grav = 10 * (6400000/(6400000+game_state['h']))**2
    a_orbit = game_state['v_x']**2/(6400000+game_state['h'])
    v_y_change = ((a_engine - a_grav + a_orbit) * dt)/10
    
    # Add acceleration values to game_state so they're sent to frontend
    game_state['v_y_change'] = v_y_change
    game_state['a_grav'] = a_grav
    game_state['a_orbit'] = a_orbit
    
    if game_state['h'] == 0:
        # Only apply engine power if it results in positive acceleration
        
        if v_y_change > 0:
            game_state['v_y'] += v_y_change
    else:
        game_state['v_y'] += v_y_change
    
    game_state['v_x'] += (total_engine_power * math.sin(alpha_rad) * dt)/10
    
    # Update position
    game_state['h'] += game_state['v_y'] * dt
    game_state['h'] = max(0, game_state['h'])  # Height can't be negative
    
    # Update fuel
    game_state['f'] -= total_engine_power * dt
    game_state['f'] = max(0, game_state['f'])  # Fuel can't be negative
    
    # Update temperatures - only if temperature difficulty is enabled
    if difficulty_settings['temperature']:
        velocity = math.sqrt(game_state['v_x']**2 + game_state['v_y']**2)
        game_state['t'] += (velocity * game_state['p'] / 100 - 2) * dt
        game_state['t'] = max(0, game_state['t'])
        
        game_state['t_l'] += (game_state['e_l'] - 1) * dt
        game_state['t_l'] = max(0, game_state['t_l'])
        
        game_state['t_r'] += (game_state['e_r'] - 1) * dt
        game_state['t_r'] = max(0, game_state['t_r'])
        
        game_state['t_c'] += game_state['sp'] * dt - 0.75 * dt
        game_state['t_c'] = max(0, game_state['t_c'])
    else:
        # Keep temperatures constant at their initial values
        game_state['t'] = initial_values['t']
        game_state['t_l'] = initial_values['t_l']
        game_state['t_r'] = initial_values['t_r']
        game_state['t_c'] = initial_values['t_c']
    
    # Update battery - only if electricity difficulty is enabled
    if difficulty_settings['electricity']:
        game_state['c'] -= 0.25 * dt
        game_state['c'] += game_state['sp'] * dt
        game_state['c'] = max(0, game_state['c'])
    else:
        # Keep battery charge constant at initial value
        game_state['c'] = initial_values['c']
    
    # Update signal level - only if connection difficulty is enabled
    if difficulty_settings['connection']:
        freq_diff = game_state['mu_in'] - game_state['mu_r']
        game_state['ls'] = min(1, game_state['ls'] - (freq_diff**2)/(game_state['mu_r']**2) + 0.01*dt)
    else:
        # Keep connection level constant at initial value
        game_state['ls'] = initial_values['ls']
    
    # Check game over conditions
    if tick_counter > 10:  # Give players some time to launch at the beginning
        if game_state['h'] == 0 and game_state['v_y'] < 0:
            game_state['game_over'] = True
            game_over = True
    
    # Check temperature-based game over conditions - only if temperature difficulty is enabled
    if difficulty_settings['temperature'] and (game_state['t'] >= 1000 or game_state['t_l'] >= 1000 or 
        game_state['t_r'] >= 1000 or game_state['t_c'] >= 1000):
        game_state['game_over'] = True
        game_over = True

    # Check connection level - only if connection difficulty is enabled
    if difficulty_settings['connection'] and game_state['ls'] < 0.01:
        game_state['game_over'] = True
        game_over = True

def game_loop():
    """
    The main game loop function that runs in the background.
    Updates the game state and broadcasts updates to all clients.
    """
    global tick_counter, counted_ticks, last_tick_time, game_running, counting_enabled, game_state
    
    # Record the start time of this tick
    current_time = time.time()
    
    # Only increment if the game is running
    if game_running:
        # Calculate time since last tick
        if last_tick_time > 0:
            elapsed = current_time - last_tick_time
            # If we're running too fast, sleep to maintain 100ms intervals
            if elapsed < 0.1:  # 100ms = 0.1s
                time.sleep(0.1 - elapsed)
        
        # Increment tick counter
        tick_counter += 1
        
        # Increment counted_ticks only if counting is enabled
        if counting_enabled:
            counted_ticks += 1
            
        # Update game state
        update_game_state()
        
        # Broadcast tick update to all clients
        socketio.emit('tick_update', {
            'ticks': tick_counter, 
            'counted_ticks': counted_ticks,
            'counting_enabled': counting_enabled
        })
        
        # Broadcast game state update
        socketio.emit('game_state_update', game_state)
    
    # Update last tick time
    last_tick_time = time.time()
    
    # Schedule the next tick (using socketio's background task system)
    socketio.start_background_task(game_loop)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True) 