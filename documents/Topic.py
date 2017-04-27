from flask_mongokit import Document
from mongokit import CustomType, IS
from datetime import datetime
from pprint import pprint

# Python 2
class CustomDate(CustomType):
    mongo_type = unicode
    python_type = datetime # optional, just for more validation
    init_type = None # optional, fill the first empty value

    def to_bson(self, value):
        """convert type to a mongodb type"""
        #pprint(value)
        return unicode(value.isoformat("T") + "Z")
        # return datetime.strptime(value, '%m-%d-%Y')

    def to_python(self, value):
        """convert type to a python object"""
        if value is not None:
           # pprint("to python : " + value)
           return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
           
           # return unicode(datetime.strftime(value,'%m-%d-%Y'))
           
           
           

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
    # default_values = {'date': datetime.utcnow}
    use_dot_notation = True


