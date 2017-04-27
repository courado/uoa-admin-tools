# from flask_pymongo import PyMongo

from flask import Flask, jsonify, request, Response

from flask_mongokit import MongoKit, Document
import json
from bson import ObjectId, json_util
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS, cross_origin

from pprint import pprint

from documents.Topic import Topic



class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'faqdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/faqdb'
mongo = MongoKit(app)
mongo.register([Topic])

@app.route('/topic', methods=['GET'])
def get_all_topics():
    topic = mongo.Topic
    output = [t for t in topic.find()]
    # return Response(dumps(output),mimetype='application/json')
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')
  

@app.route('/topic', methods=['DELETE'])
def delete_all_topics():
    topic = mongo.Topic
    mongo.Topic.collection.remove()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/topic/<string:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = mongo.Topic
    topic = mongo.Topic.find_one({'_id': ObjectId(topic_id) })
    topic.delete()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/topic/<string:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = mongo.Topic.find_one({'_id': ObjectId(topic_id) })
    return Response(json.dumps(topic,cls=ComplexEncoder),mimetype='application/json')

@app.route('/topic', methods=['POST'])
def add_topic():
    topic = mongo.Topic.from_json(str(request.data))
    topic.save()
    return Response(json.dumps(topic,cls=ComplexEncoder),mimetype='application/json')



if __name__ == '__main__':
	app.run(debug=True)
