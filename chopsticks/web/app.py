from flask import Flask, session, render_template
from flask_session import Session  # type: ignore

from chopsticks.core import Game
from chopsticks.move import Move, Hit, Split

app = Flask("Chopsticks Game",
            static_folder='chopsticks/web/static',
            template_folder='chopsticks/web/templates')

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route("/")  # type: ignore
def hello():
    g: Game|None = session.get('game')  # type: ignore
    if not g:
        g = Game(2, 5, ['H', 'RB'])
        session['game'] = g

    return render_template("index.html")

@app.route("/state")  #type: ignore
def get_state():
    g: Game = session.get('game')  # type: ignore
    state = g.state
    return {
        "state": state.to_json(),
    }

@app.route('/play', defaults={'move_code': None})  # type: ignore
@app.route("/play/<move_code>")  # type: ignore
def play(move_code: str):
    g: Game|None = session.get('game')  # type: ignore
    if not g:
        g = Game(2, 5, ['H', 'RB'])
        session['game'] = g

    content: str = g.ui.get_game_state(g.state)
    if move_code:
        move: Move = _parse_move(move_code)
        content += f"<br/>you moved: {move}"
        g.play_async(move)
        content += f"<br/>Now:<br/>{g.ui.get_game_state(g.state)}"

    return content

def _parse_move(move_code: str) -> Move:
    ui_list = move_code.strip().lower().split(',')
    
    if ui_list[0] in [Hit.code, 'hit']:
        #Input: Hit, PLayerBeingHit, GivingHand, ReceivingHand
        return Hit(int(ui_list[1]), int(ui_list[2]), int(ui_list[3]))
    elif ui_list[0] in [Split.code,'split']:
        #Input: Split, Hand1, Hand2, Amount1, Amount2
        return Split(int(ui_list[1]), int(ui_list[2]), int(ui_list[3]), int(ui_list[4]))
    else:
        raise Exception(f"unknown move type: {move_code}")


@app.route("/reset") # type: ignore
def reset():
    del session['game']
    return 'session deleted'
