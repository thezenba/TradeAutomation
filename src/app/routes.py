from flask import render_template, jsonify
from .app import app
import subprocess
import threading
import src.main
import src.backtests
import os
import signal

BOT_RUNNING = False
bot_process = None


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/start_bot', methods=['POST'])
def start_bot():
    global BOT_RUNNING
    global bot_process
    if BOT_RUNNING:
        return jsonify({'error': 'Bot is already running'}), 400
    BOT_RUNNING = True
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True  # Allow the main program to exit even if the thread is running
    bot_thread.start()
    return jsonify({'message': 'Bot started'})


def run_bot():
    global bot_process
    try:
        bot_process = subprocess.Popen(["python", "src/main.py"])
        bot_process.wait()
    finally:
        global BOT_RUNNING
        BOT_RUNNING = False


@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    global BOT_RUNNING
    global bot_process
    if not BOT_RUNNING or bot_process is None:
        return jsonify({'error': 'Bot is not running'}), 400
    os.kill(bot_process.pid, signal.SIGTERM)
    BOT_RUNNING = False
    return jsonify({'message': 'Bot stopped'})


@app.route('/start_backtest', methods=['POST'])
def start_backtest():
    subprocess.Popen(["python", "src/backtests.py"])
    return jsonify({'message': 'Backtest started'})