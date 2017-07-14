from flask_mongokit import Document

class Page(Document):
    __collection__ = 'pages'
    structure = {
        'route' : unicode,
        'name' : unicode
    }
    required_fields = ['route', 'name']
    use_dot_notation = True