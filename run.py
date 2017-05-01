# from flask_pymongo import PyMongo

from flask import Flask, jsonify, request, Response

from flask_mongokit import MongoKit, Document
import json
from bson import ObjectId, json_util
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS, cross_origin

from pprint import pprint

from documents import Topic, Question



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
mongo.register([Topic,Question])

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

@app.route('/topic', methods=['POST',])
def add_topic():
    topic = mongo.Topic()
    topic.update(mongo.Topic.from_json(str(request.data)))
    topic.weight = float(topic.weight)
    topic.save()
    return Response(json.dumps(topic,cls=ComplexEncoder),mimetype='application/json')

@app.route('/question', methods=['GET'])
def get_all_questions():
    question = mongo.Question
    output = [t for t in question.find()]
    # return Response(dumps(output),mimetype='application/json')
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')
  
@app.route('/question', methods=['DELETE'])
def delete_all_questions():
    question = mongo.Question
    mongo.Question.collection.remove()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/question/<string:question_id>', methods=['DELETE'])
def delete_question(question_id):
    question = mongo.Question
    question = mongo.Question.find_one({'_id': ObjectId(question_id) })
    question.delete()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/question/<string:question_id>', methods=['GET'])
def get_question(question_id):
    question = mongo.Question.find_one({'_id': ObjectId(question_id) })
    return Response(json.dumps(question,cls=ComplexEncoder),mimetype='application/json')

@app.route('/question', methods=['POST',])
def add_question():
    question = mongo.Question()
    request.json['hello'] = 'hello'
    pprint(request.data)
    pprint(request.json)
    for topic in request.json['topics']:
        topic = ObjectId(topic)
    print("----------------------")
    pprint(request.data)
    question.update(mongo.Question.from_json(str(request.data)))
    for topic in question['topics']:
        pprint(topic)
        topic = ObjectId(topic)
        pprint(topic)
    question.save()
    return Response(json.dumps(question,cls=ComplexEncoder),mimetype='application/json')



if __name__ == '__main__':
	app.run(debug=True,host='0.0.0.0')
