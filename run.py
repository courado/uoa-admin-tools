# from flask_pymongo import PyMongo

from flask import Flask, jsonify, request, Response, abort
import os
from flask_mongokit import MongoKit, Document
import json
from bson import ObjectId, json_util
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS, cross_origin

from pprint import pprint

from documents import Topic, Question

import time

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME','faqdb')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI','mongodb://localhost:27017/faqdb')
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME','localhost:5000')
app.config['DEBUG'] = str2bool(os.environ.get('DEBUG','False'))

mongo = MongoKit(app)
mongo.register([Topic,Question])

#===========
#  TOPICS 
#===========

def delete_topic_questions(topic):
    # pprint(topic)
    questions = mongo.Question.find({"topics" : topic._id})
    
    for question in questions:
        question.topics.remove(topic._id)
        if len(question.topics)==0 :
            question.delete()
        else:
            question.save()



@app.errorhandler(Exception)
def all_exception_handler(error):
   return jsonify({"error" : str(error)})

@app.route('/topic', methods=['GET'])
def get_all_topics():
    topic = mongo.Topic
    output = [t for t in topic.find()]
    # return Response(dumps(output),mimetype='application/json')
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')
  
@app.route('/topic/delete', methods=['POST'])
def delete_selected_topics():
    ids = [ObjectId(id) for id in request.json]
    topics = mongo.Topic.find({"_id" : {"$in" : ids}})
    deleted = []
    for topic in topics:
        delete_topic_questions(topic)
        deleted.append(topic._id)
        topic.delete()
    return Response(json.dumps({"deleted" : deleted},cls=ComplexEncoder),mimetype='application/json')

@app.route('/topic', methods=['DELETE'])
def delete_all_topics():
    mongo.Topic.collection.remove()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/topic/<string:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    topic = mongo.Topic
    topic = mongo.Topic.find_one({'_id': ObjectId(topic_id) })
    delete_topic_questions(topic)

    topic.delete()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/topic/<string:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = mongo.Topic.find_one({'_id': ObjectId(topic_id) })
    return Response(json.dumps(topic,cls=ComplexEncoder),mimetype='application/json')

@app.route('/topic', methods=['POST'])
def add_topic():
    topic = mongo.Topic()
    topic.update(mongo.Topic.from_json(str(request.data)))
    topic.weight = float(topic.weight)
    if "_id" in request.json:
        topic["_id"] = ObjectId(request.json["_id"])
    topic.save()
    return Response(json.dumps(topic,cls=ComplexEncoder),mimetype='application/json')

@app.route('/topic/toggle', methods=['POST'])
def status_topic():
    order = request.args.get('order')
    if order not in (u'hits',u'weight'):
        raise Exception('Not hits or weight')
    topics_ids = [ObjectId(t) for t in request.json]
    question = mongo.Topic.collection.update({'_id': {"$in" : topics_ids }}, {'$set':{'questionOrder': order}}, multi = True)
    return Response(json.dumps(topics_ids,cls=ComplexEncoder),mimetype='application/json')

#===========
# QUESTIONS 
#===========

def resolve_topics(question) :
    for i,item in enumerate(question.topics):
        question.topics[i] = mongo.Topic.find_one({"_id" : item})
    return question

@app.route('/question', methods=['GET'])
def get_all_questions():
    question = mongo.Question
    questions = [t for t in question.find()]
    [resolve_topics(question) for question in questions]
    return Response(json.dumps(questions,cls=ComplexEncoder),mimetype='application/json')
  
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
    question = resolve_topics(question)
    return Response(json.dumps(question,cls=ComplexEncoder),mimetype='application/json')

@app.route('/question', methods=['POST'])
def add_question():
    question = mongo.Question()
    topics_ids = []
    for i,item in enumerate(request.json['topics']):
        request.json['topics'][i] = ObjectId(item)
    question.update(request.json)
    question.weight = float(question.weight)
    if "_id" in request.json:
        question["_id"] = ObjectId(request.json["_id"])
    question.save()
    resolve_topics(question)
    return Response(json.dumps(question,cls=ComplexEncoder),mimetype='application/json')

@app.route('/question/delete', methods=['POST'])
def delete_question_selected():
    ids = [ObjectId(id) for id in request.json]
    questions = mongo.Question.find({"_id" : {"$in" : ids}})
    deleted = []
    for question in questions:
        deleted.append(question._id)
        question.delete()
    return Response(json.dumps(deleted,cls=ComplexEncoder),mimetype='application/json')

@app.route('/question/toggle', methods=['POST'])
def status_question():
    if request.args.get('status') == None :
        raise Exception('Provide a toggle status (true,false)')
    status = str2bool(request.args.get('status'))
    question_ids = [ObjectId(t) for t in request.json]
    question = mongo.Question.collection.update({'_id': {"$in" : question_ids }}, {'$set':{'isActive': status}}, multi = True)
    return Response(json.dumps(question_ids,cls=ComplexEncoder),mimetype='application/json')
# 
if __name__ == '__main__':
	app.run()
