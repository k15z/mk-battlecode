import json
import string
import requests
import argparse
from random import choice
from subprocess import call, check_output

parser = argparse.ArgumentParser(description="Launch a new worker node which interacts with the cluster at the given host/port.")
parser.add_argument("base_url", type=str, help="host:port (ex: mk.kevz.me:3000)")
parser.add_argument("--nb_matches", type=int, default=5, help="number of matches to run")
args = parser.parse_args()

worker_id = name = ''.join(choice(string.ascii_lowercase) for i in range(8))

maps = list()
for line in check_output(["gradle", "listMaps"]).decode("utf8").split("\n"):
    if "MAP:" in line:
        maps.append(line.replace("MAP:", "").strip())

def load_player(player):
    dst = "src/" + player + ".zip"
    with open(dst, 'wb') as f:
        f.write(requests.get(url=args.base_url+"/player/" + player).content)
    call(["unzip", "-o", dst, "-d", "src/"])
    call(["rm", dst])

def new_match():
    res = requests.get(url=args.base_url+"/new_match")
    obj = json.loads(res.text)
    playerA, playerB = obj["playerA"], obj["playerB"]

    load_player(playerA)
    load_player(playerB)
    return playerA, playerB, choice(maps)

def run_match(match_nb):
    playerA, playerB, _map = new_match()
    logs = check_output(["gradle", "run", "-PteamA="+playerA, "-PteamB="+playerB, "-Pmaps="+_map])

    report = {}
    report["meta"] = {}
    report["map"] = _map
    for line in logs.decode("utf8").split("\n"):
        if "wins (" in line:
            log = line.replace("[server]", "").strip()
            report["meta"]["log"] = log
            if playerA in log:
                report["winner"] = playerA
                report["loser"] = playerB
            elif playerB in log:
                report["winner"] = playerB
                report["loser"] = playerA
    requests.post(url=args.base_url+"/match_results", json=report)
    print(report)

match_nb = 0
while args.nb_matches == -1 or args.nb_matches > match_nb:
    run_match(match_nb)
    match_nb += 1
