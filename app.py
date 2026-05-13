"""Flask application — serves the Tetris frontend and exposes engine API."""

from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/state')
def api_state():
    """Placeholder — will be wired to TetrisEngine.get_state() when backend is ready."""
    return jsonify({
        'grid': [[0] * 10 for _ in range(20)],
        'score': 0,
        'level': 1,
        'lines_cleared': 0,
        'current_piece': None,
        'next_piece': None,
        'game_over': False,
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
