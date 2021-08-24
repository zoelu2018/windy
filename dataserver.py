#!/usr/bin/python
# coding:utf-8

from flask import Flask, jsonify
from flask_cors import *
from flask_restful import reqparse, abort, Api, Resource
from sys import argv
import json
import os

app = Flask(__name__)
CORS(app, resources='/*')
api = Api(app=app)
parser = reqparse.RequestParser()
parser.add_argument('date', location='args', required=True)
parser.add_argument('mb', location='args', required=True)

def files_nofind():
    abort(404, message='files not found')

class ToGetData(Resource):
    def get(self):
        req = parser.parse_args(strict=True)
        date, mb = req.get('date'), req.get('mb')
        with open('./resource/config.json') as jsonfile:
            config = json.load(jsonfile)

        files = [f for f in os.listdir(config['inputpath']) if date in f and mb in f]
        if len(files) == 0:
            print '未找到文件'
            files_nofind()
        with open(os.path.join(config['inputpath'],files[0])) as datafile:
            data = json.load(datafile)
        return data

api.add_resource(ToGetData, '/getdata')   

if __name__ == '__main__':
    if len(argv) > 1:
        app.run(host='0.0.0.0', port=int(argv[1]), debug=False, threaded=False, processes=4)
    else:
        app.run(host='0.0.0.0', port=4500, debug=False, threaded=False, processes=4)