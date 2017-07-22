import os
import re
import sys
import json
import string
import argparse
import requests
from subprocess import call
from random import choice, random
from modeling import create_better_parameters

parser = argparse.ArgumentParser(description="Launch a new worker node which interacts with the cluster at the given host/port.")
parser.add_argument("mode", type=str, help="host:port (ex: mk.kevz.me:3000)")
parser.add_argument("base_url", type=str, help="host:port (ex: mk.kevz.me:3000)")
args = parser.parse_args()

TALIA_FLOAT_RE = "TALIA_FLOAT\([^\)]*\)"

def get_talia():
    with open(".talia", "rt") as fin:
        return json.load(fin)

def set_talia(talia):
    with open(".talia", "wt") as fout:
        json.dump(talia, fout)

def parse_min_max(talia_float_str):
    return map(float, talia_float_str.replace("TALIA_FLOAT(", "")[:-1].split(","))

def init():
    with open("RobotPlayer.java", "rt") as fin:
        template = fin.read()

    parameters = {}
    while re.findall(TALIA_FLOAT_RE, template):
        key = ''.join(choice(string.ascii_lowercase) for i in range(8))
        param_name = "TALIA_PLACEHOLDER_" + key
        parameters[param_name] = tuple(parse_min_max(re.findall("TALIA_FLOAT\([^\)]*\)", template)[0]))
        template = re.sub(TALIA_FLOAT_RE, param_name, template, 1)

    with open(".talia", "wt") as fout:
        json.dump({
            "template": template,
            "parameters": parameters,
            "agents": {}
        }, fout)

def apply_params(code, parameters):
    for param_name, value in parameters.items():
        code = code.replace(param_name, str(value) + "f")
    return code

def create_bot(talia, name, parameters):
    code = "package " + name + "; //" + talia["template"]
    code = apply_params(code, parameters)

    os.makedirs("agents/" + name)
    with open("agents/" + name + "/RobotPlayer.java", "wt") as fout:
        fout.write(code)
    os.system("cd agents && zip -r " + name + " " + name)
    call(["curl", "-F", "player=@agents/" + name + ".zip", args.base_url + "/player/" + name])
    call(["rm", "-rf", "agents/" + name])

def generate():
    talia = get_talia()

    name = ''.join(choice(string.ascii_lowercase) for i in range(8))
    parameters = {k: random() * (v[1] - v[0]) + v[0] for k, v in talia["parameters"].items()}
    talia["agents"][name] = parameters
    create_bot(talia, name, parameters)

    set_talia(talia)

def status():
    rankings = requests.get(url=args.base_url+"/rankings").json()
    print("\n".join(map(str, reversed(sorted([(ranking["mu"], ranking["sigma"], player_id)for player_id, ranking in rankings.items()])))))

def learned():
    talia = get_talia()
    rankings = requests.get(url=args.base_url+"/rankings").json()

    dataset = {}
    for player_id, ranking in rankings.items():
        if player_id in talia["agents"]:
            dataset[player_id] = {
                "ranking": ranking["mu"],
                "parameters": talia["agents"][player_id]
            }

    for parameters in create_better_parameters(dataset, talia["parameters"]):
        name = ''.join(choice(string.ascii_lowercase) for i in range(8)) + "_tf6"
        talia["agents"][name] = parameters

        create_bot(talia, name, parameters)
        set_talia(talia)

if args.mode == "init":
    init()
    for i in range(10):
        generate()
if args.mode == "status":
    status()
if args.mode == "learn":
    learned()
