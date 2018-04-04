#!/usr/bin/env python

from flask import Flask, jsonify

app = Flask(__name__)
app.debug = True



@app.route("/")
def test():
    return jsonify({1: "ein", 2: "schluessel", 3: "fuer", 4: "schloesser"})


@app.route("/games")
def listGames():
    return jsonify({1: "quake", 2: "DotA"})

app.run()


