import os
import shutil
import argparse
from random import shuffle
from trueskill import Rating, rate_1vs1
from bottle import get, post, run, abort, request, static_file

parser = argparse.ArgumentParser(description="Launch a cluster node which provides a HTTP API for managing bots.")
parser.add_argument("--port", type=int, default=3000, help="number of matches to run")
args = parser.parse_args()

ROOT = "bots"
if os.path.exists(ROOT):
    shutil.rmtree(ROOT)
os.makedirs(ROOT)

bots = {}

@get('/rankings')
def get_rankings():
    return {bot: {"mu": ranking.mu, "sigma": ranking.sigma} for bot, ranking in bots.items()}

@get('/new_match')
def get_new_match():
    if len(bots) < 2:
        abort(503, "Not enough players!")
    uncertainties = [(ranking.sigma, bot) for bot, ranking in bots.items()]
    uncertain_bots = list(map(lambda x: x[1], list(reversed(sorted(uncertainties)))[:5]))
    shuffle(uncertain_bots)
    return { "playerA": uncertain_bots[0], "playerB": uncertain_bots[1] }

@post("/match_results")
def post_match_results():
    winner, loser = request.json["winner"], request.json["loser"]
    bots[winner], bots[loser] = rate_1vs1(bots[winner], bots[loser])
    return {"accepted": True}

@get("/player/:player_id")
def get_player(player_id):
    return static_file(player_id + ".zip", root=ROOT)

@post("/player/:player_id")
def post_player(player_id):
    request.files.get('player').save(ROOT + "/" + player_id + ".zip")
    bots[player_id] = Rating()
    return {"accepted": True}

run(host='0.0.0.0', port=args.port)
