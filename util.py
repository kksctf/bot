import json
import time

def load_settings(filename="config.json"):
    with open(filename) as fin:
        settings = json.load(fin)
    return settings


def panic(s):
    with open(f"panic{int(time.time())}", "w") as fout:
        fout.write(s)

    exit(1)
