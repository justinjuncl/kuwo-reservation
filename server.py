#!flask/bin/python

import json
from functools import reduce

from flask import Flask, jsonify, abort, make_response
from flask_cors import CORS, cross_origin
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__, static_url_path="")
CORS(app)
api = Api(app)

def save():
    with open('data.json', 'w') as f:
        data = {
            'mbr': mbr,
            'xy': xy
        }
        json.dump(data, f)

def load():
    with open('data.json', 'r') as f:
        global xy, mbr
        data = json.load(f)
        xy = data['xy']
        mbr = data['mbr']

def train():
    global mbr
    x = []
    y = []

    for key in xy:
        x.append(key['x'])
        y.append(key['y'])

    xSum = reduce((lambda a, b: a + b), x)
    xBar = xSum / len(x)

    ySum = reduce((lambda a, b: a + b), y)
    yBar = ySum / len(y)

    xDiff = list(map(lambda a: a - xBar, x))
    yDiff = list(map(lambda a: a - yBar, y))

    xDiffyDiff = list(map(lambda a, b: a * b, xDiff, yDiff))

    xDiffSq = list(map(lambda a: a * a, xDiff))
    yDiffSq = list(map(lambda a: a * a, yDiff))

    xDiffyDiffSum = reduce((lambda a, b: a + b), xDiffyDiff)
    xDiffSqSum = reduce((lambda a, b: a + b), xDiffSq)
    yDiffSqSum = reduce((lambda a, b: a + b), yDiffSq)

    m = xDiffyDiffSum / xDiffSqSum
    b = yBar - m * xBar
    r = ( xDiffyDiffSum * xDiffyDiffSum ) / ( xDiffSqSum * yDiffSqSum )

    mbr = {
        'm': m,
        'b': b,
        'r': r
    }

    print(m, b, r)
    save()

class MBRAPI(Resource):
    def get(self):
        return {'mbr': mbr}

class XYAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('x', type=int, required=True, location='json')
        self.reqparse.add_argument('y', type=int, required=True, location='json')
        super(XYAPI, self).__init__()

    def get(self):
        return {'xy': xy}

    def post(self):
        args = self.reqparse.parse_args()
        newXY = {
            'x': args['x'],
            'y': args['y']
        }
        xy.append(XY)
        train()
        return {'result': True}

class AllAPI(Resource):
    def get(self):
        return {'mbr': mbr, 'xy': xy}

api.add_resource(MBRAPI, '/mbr/', endpoint='mbr')
api.add_resource(XYAPI, '/xy/', endpoint='xy')
api.add_resource(AllAPI, '/all/', endpoint='all')

if __name__ == '__main__':
    load()
    train()
    app.run(debug=True)
