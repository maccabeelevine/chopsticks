from flask import Flask, request, session, render_template
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
        "last_move": g.last_move.to_json() if g.last_move else None,
    }

@app.route("/move", methods=['POST'])  # type: ignore
def play():
    g: Game = session.get('game')  # type: ignore
    move_code = request.data.decode("utf-8") 
    if move_code:
        move: Move = _parse_move(move_code)
        g.play_async(move)
        return {
            "last_move": move.to_json(),
        }
        
    else:
        return "Invalid Move", 400

@app.route("/botMove", methods=['POST'])  #type: ignore
def botMove():
    g: Game = session.get('game')  # type: ignore
    g.play_async(None)
    return ""

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
