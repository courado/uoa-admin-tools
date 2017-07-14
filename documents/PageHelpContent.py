from flask_mongokit import Document
from mongokit import CustomType, IS
from datetime import datetime
from pprint import pprint
from CustomDate import CustomDate
from bson.objectid import ObjectId

class PageHelpContent(Document):
    __collection__ = 'pageHelpContents'
    structure = {
        'page' : ObjectId,
        'placement' : IS(u"top",u"bottom",u"right",u"left"),
        'order': int,
        'content': unicode,
        'isActive' : bool
    }
    required_fields = ['page', 'placement','order','isActive']
    default_values = {'isActive' : True }
    use_dot_notation = True