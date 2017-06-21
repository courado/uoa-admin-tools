from flask_mongokit import Document
from mongokit import CustomType, IS
from datetime import datetime
from pprint import pprint
from CustomDate import CustomDate

class Topic(Document):
    __collection__ = 'topics'
    structure = {
        'name' : unicode,
        'description' : unicode,
        'date' : CustomDate(),
        'weight' : float,
        'questionOrder' : IS(u"hits",u"weight")
    }
    required_fields = ['name','weight','questionOrder']
    default_values = {'date': datetime.utcnow}
    use_dot_notation = True


