# from flask_pymongo import PyMongo
from flask import Flask, jsonify, request, Response, abort, send_file
import os
from flask_mongokit import MongoKit, Document
import json
from bson import ObjectId, json_util
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS, cross_origin
from pprint import pprint
from documents import Topic, Question, Page, PageHelpContent
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
# 
app = Flask(__name__)

app.config['MONGODB_HOST'] = os.environ.get('MONGODB_HOST','194.177.192.227')
app.config['MONGODB_USERNAME'] = os.environ.get('MONGODB_USERNAME',None)
app.config['MONGODB_PASSWORD'] = os.environ.get('MONGODB_PASSWORD',None)
app.config['MONGODB_PORT'] = int(os.environ.get('MONGODB_PORT','27017'))
app.config['MONGODB_DATABASE'] = os.environ.get('MONGODB_DATABASE','faqs')
# app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME','localhost:5000')
app_port = int(os.environ.get('APP_PORT','5000'))
app.config['DEBUG'] = str2bool(os.environ.get('DEBUG','True'))
CORS(app)
mongo = MongoKit(app)

mongo.register([Topic,Question,Page,PageHelpContent])

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
   return Response(json.dumps({"error" : str(error)}),mimetype='application/json',status=500)

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

def resolve_questions(topic) :
    question = mongo.Question;
    orderby = "hitCount" if(topic.questionOrder == 'hits') else 'weight'
    pprint(topic._id)
    topic['questions'] = [t for t in question.find({'topics' : topic._id, 'isActive' : True },sort=[(orderby,-1)])]
    return topic

@app.route('/topic/active', methods=['GET'])
def get_active_topics ():
    topic = mongo.Topic
    output = [resolve_questions(t) for t in topic.find()]
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')

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

@app.route('/question/inc/<string:question_id>', methods=['PUT'])
def inc_question(question_id):
    question = mongo.Question.find_and_modify({'_id': ObjectId(question_id) },{'$inc' : {'hitCount' : 1}}, new= True)
    return Response(json.dumps(question,cls=ComplexEncoder),mimetype='application/json')

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

#===========
# PAGE
#===========

@app.route('/test', methods=['GET'])
def getTest():
    mongo.connect()
    return str(mongo.connected)


@app.route('/page', methods=['GET'])
def get_all_pages():
    page = mongo.Page
    output = [t for t in page.find()]
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')

@app.route('/page', methods=['POST'])
def add_page():
    page = mongo.Page()
    page.update(mongo.Page.from_json(str(request.data)))
    if "_id" in request.json:
        page["_id"] = ObjectId(request.json["_id"])
    page.save()
    return Response(json.dumps(page,cls=ComplexEncoder),mimetype='application/json')

@app.route('/page/delete', methods=['POST'])
def delete_pages_selected():
    ids = [ObjectId(id) for id in request.json]
    questions = mongo.Page.find({"_id" : {"$in" : ids}})
    deleted = []
    for question in questions:
        deleted.append(question._id)
        question.delete()
    return Response(json.dumps(deleted,cls=ComplexEncoder),mimetype='application/json')

@app.route('/page/route', methods=['GET'])
def get_page():
    if request.args.get('q') == None :
        raise Exception('Provide the route parameter <q>')
    page_name = request.args.get('q')
    page = mongo.Page.find_one({'route': page_name })
    page['content'] = {'top' :[], 'left' :[], 'right' : [], 'bottom': []}
    for content in mongo.PageHelpContent.find({'page' : page._id, 'isActive' : True},sort=[('order',-1)]):
        page['content'][content.placement].append(content)
    #question = resolve_topics(question)
    return Response(json.dumps(page,cls=ComplexEncoder),mimetype='application/json')

#===================
# PAGE HELP CONTENT
#===================

def resolve_pages(pageHelpContent):
    pageHelpContent.page = mongo.Page.find_one({'_id': pageHelpContent["page"] })
    return pageHelpContent

@app.route('/pagehelpcontent', methods=['GET'])
def get_all_pagehelpcontents():
    page = mongo.PageHelpContent
    output = [resolve_pages(t) for t in page.find()]
    return Response(json.dumps(output,cls=ComplexEncoder),mimetype='application/json')

@app.route('/pagehelpcontent/<string:pagehelpcontent_id>', methods=['GET'])
def get_pagehelpcontent(pagehelpcontent_id):
    pagehelpcontent = mongo.PageHelpContent.find_one({'_id': ObjectId(pagehelpcontent_id) })
    #question = resolve_topics(question)
    return Response(json.dumps(pagehelpcontent,cls=ComplexEncoder),mimetype='application/json')

@app.route('/pagehelpcontent', methods=['POST'])
def add_pagehelpcontents():
    page = mongo.PageHelpContent()
    request.json["page"] = ObjectId(request.json["page"])
    request.json["order"] = int(request.json["order"])
    page.update(request.json)
    if "_id" in request.json:
        page["_id"] = ObjectId(request.json["_id"])
    page.save()
    return Response(json.dumps(page,cls=ComplexEncoder),mimetype='application/json')

@app.route('/pagehelpcontent/delete', methods=['POST'])
def delete_pagehelpcontents_selected():
    ids = [ObjectId(id) for id in request.json]
    questions = mongo.PageHelpContent.find({"_id" : {"$in" : ids}})
    deleted = []
    for question in questions:
        deleted.append(question._id)
        question.delete()
    return Response(json.dumps(deleted,cls=ComplexEncoder),mimetype='application/json')

@app.route('/pagehelpcontent', methods=['DELETE'])
def delete_all_pagehelpcontents():
    pagehelpcontents = mongo.PageHelpContent
    pagehelpcontents.collection.remove()
    return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/pagehelpcontent/toggle', methods=['POST'])
def status_pagehelpcontent():
    if request.args.get('status') == None :
        raise Exception('Provide a toggle status (true,false)')
    status = str2bool(request.args.get('status'))
    pagehelpcontent_ids = [ObjectId(t) for t in request.json]
    question = mongo.PageHelpContent.collection.update({'_id': {"$in" : pagehelpcontent_ids }}, {'$set':{'isActive': status}}, multi = True)
    return Response(json.dumps(pagehelpcontent_ids,cls=ComplexEncoder),mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=app_port)

