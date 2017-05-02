from flask_mongokit import Document
from mongokit import CustomType, IS
from datetime import datetime
from pprint import pprint
from CustomDate import CustomDate
from bson.objectid import ObjectId

class Question(Document):
    __collection__ = 'questions'
    structure = {
        'question' : unicode,
        'answer' : unicode,
        'date' : CustomDate(),
        'isActive' : bool,
        'weight' : float,
        'hitCount' : int,
        'topics' : [ObjectId]
    }
    required_fields = ['question', 'answer','isActive','weight','hitCount','topics']
    default_values = {'date': datetime.utcnow, 'hitCount' : 0, 'isActive' : True }
    use_dot_notation = True

