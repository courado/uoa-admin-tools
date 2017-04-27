# from flask_pymongo import PyMongo

from flask import Flask, jsonify, request, Response

from flask_mongokit import MongoKit, Document
from mongokit import CustomType, IS
import json
from bson import ObjectId, json_util
from bson.json_util import dumps
from datetime import datetime
from flask_cors import CORS, cross_origin

from pprint import pprint

# Python 2
class CustomDate(CustomType):
    mongo_type = datetime
    python_type = unicode # optional, just for more validation
    init_type = None # optional, fill the first empty value

    def to_bson(self, value):
        """convert type to a mongodb type"""
        return datetime.strptime(value, '%m-%d-%Y')

    def to_python(self, value):
        """convert type to a python object"""
        if value is not None:
           return unicode(datetime.strftime(value,'%m-%d-%Y'))
           

    def validate(self, value, path):
        """OPTIONAL : useful to add a validation layer"""
        if value is not None:
            pass # ... do something here

class Topic(Document):
    __collection__ = 'tasks'
    structure = {
        'name' : unicode,
        'description' : unicode,
        'date' : CustomDate(),
        'weight' : float,
        'questionOrder' : IS(u"hits",u"weight")
    }
    required_fields = ['name', 'description','weight','questionOrder']
    default_values = {'date': datetime.utcnow}
    use_dot_notation = True

    def make_id(self):
    	pprint(self)
    	self['id'] = str(self._id)
    	return self



app = Flask(__name__)
CORS(app)
app.config['MONGO_DBNAME'] = 'faqdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/faqdb'
mongo = MongoKit(app)
mongo.register([Topic])

@app.route('/topic', methods=['GET'])
def get_all_topics():
  topic = mongo.Topic
  output = [t.make_id() for t in topic.find()]
  return Response(dumps(output),mimetype='application/json')

@app.route('/topic', methods=['DELETE'])
def delete_all_topics():
  topic = mongo.Topic
  mongo.Topic.collection.remove()
  return Response(dumps({"status" : "OK"}),mimetype='application/json')

@app.route('/topic/<string:topic_id>', methods=['GET'])
def get_topic(topic_id):
    topic = mongo.Topic.find_one({'_id': ObjectId(topic_id) })
    return Response(dumps(topic),mimetype='application/json')

@app.route('/topic', methods=['POST'])
def add_topic():
  topic = mongo.Topic.from_json(str(request.data))
  topic.save()
  return Response(dumps(topic),mimetype='application/json')



if __name__ == '__main__':
	app.run(debug=True)
