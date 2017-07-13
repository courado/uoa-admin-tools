# Application Overview

The micro service consists of a back-end (Flask Application) and the front-end (Angular2) communicating over rest API.

```
+-------------+              +-------------+                +-------------+
|             |              |             |                |             |
|  mongo-db   |  <--http-->  |  back-end   |  <---REST--->  |  front-end  |
|             |              |             |                |             |
+-------------+              +-------------+                +-------------+
```
# Docker deployment

The `back-end` and `front-end` can be easily wrapped in an nginx server using the privided `Dockerfile` that uses `uWGSI` to serve the `back-end`'s' API and standard nginx for the `front-end`.


The application for ease of use can be deployed as a single docker swarm application with the provided `docker-compose.yml` file. This method of deployment, starts alongside the application an official `mongodb` instance, linking the applications together.

`docker stack deploy -c docker-compose.yml <stack_name>`.

## Front-end build

In order to build the Docker for production, the `git submodule` has to be initiated and pulled in the `front-end` folder. Inside the `front-end/webpack.config.js` change the `API_ENDPOINTS` to hit the back-end's ip and port, postfixed with the `/api` path.

Example  :
```js
new webpack.DefinePlugin({"process.env" : {
    PRODUCTION: JSON.stringify(true),
    API_ENDPOINT : JSON.stringify(process.env.API_ENDPOINT || "my.example.com"),
    API_PORT : JSON.stringify(process.env.API_PORT || "80"),
    API_PATH : JSON.stringify("/api")
}})
```
Finally build the angular application using the following steps :

1. `npm i` (first time only).
2. `npm run build:prod`
3. `npm start` for development

## Docker build (back / frond -end)

Simply invoke the docker build command and push it to a docker repository :

1. `docker build . -t <repository>:<port>/<name>`
2. `docker push <repository>:<port>/<name>`

## Back-end settings
Changes can be changed easily by providing the following environment variables either with `EXPORT` or `docker -e` command.
```properties
MONGODB_HOST     = my.example.com
MONGODB_USERNAME = None  #if set
MONGODB_PASSWORD = None  #if set
MONGODB_PORT     = 27017
MONGODB_DATABASE = faq
APP_PORT         = 5000
DEBUG            = True | False

```

## Back-end requirements
Have `Python 2.7` installed alongside `pip`
Install the required packages using `pip install --upgrade -r requirements.txt`

## Back-end execution
When run in debug mode, for every file change detected the application will recompile itself and restart. Only syntactic errors will cause the application to crush.

To run the application execute :
```bash
python main.py
```

## Documents
The following documents are currently served : 

```
+----------+              +-------------+ 
|          |  *        1  |             | 
|  Topic   |  <-------->  |  Question   | 
|          |              |             | 
+----------+              +-------------+ 
```

### Topic
Creates a topic category in which question are attached. 

#### Structure
```json
{
	"name" : "str",
	"description" : "str",
	"date" : "date",
	"weight" : "float",
	"questionOrder" : "hits | weight"
}
```

Required : 
1. `name`
2. `description`
3. `questionOrder`

#### API

`GET /topic` returns all topics

Example Response :

```json
[
    {
        "name": "Legal",
        "weight": 5,
        "questionOrder": "hits",
        "date": "2017-06-29T12:00:19.987768",
        "_id": "594a917a01f55e000ff95b3d",
        "description": "Information on Legal issues with questions and answers"
    },
    {
        "name": "Guidelines",
        "weight": 5,
        "questionOrder": "weight",
        "date": "2017-06-30T12:00:19.987768",
        "_id": "594a917a01f55e000ff95b3e",
        "description": "Information on guidelines issues with questions and answers"
    }
]

```

----------------------------------------------------------

`GET /topic/<id>` return the topic with the requested id

Example : `GET /topic/594a917a01f55e000ff95b3e`

Reponse body :

```json
{
    "name": "Guidelines",
    "weight": 5,
    "questionOrder": "weight",
    "date": "2017-06-30T12:00:19.987768",
    "_id": "594a917a01f55e000ff95b3e",
    "description": "Information on guidelines issues with questions and answers"
}
```
----------------------------------------------------

`POST /topic` creates a new topic or updates an existing one if the `_id` is supplied.

Example Body : 

```json
{
    "name": "New Topic",
    "weight": 1,
    "questionOrder": "weight",
    "description": "Description of the topic"
}
```

Example Response : (`OK 200` else `ERROR 500`)
```json
{
    "name": "New Topic",
    "weight": 1,
    "questionOrder": "weight",
    "date": "2017-06-30T12:00:19.987768",
    "_id": "594a917a01f55e000ff95b3f",
    "description": "Description of the topic"
}
```

---------------------------------------------
`DELETE /topic` deletes all topics

-----------------------------------------------

`DELETE /topic/<id>` deletes the topic with the id removing itself from the questions referenced by that topic. If a question is left with no related topic, the delete operation is cascaded to that question.

Example `DELETE /topic/594a917a01f55e000ff95b3f`

---------------------------------------------

`GET /topics/active` return all the topics with their referenced question that are active. The questions are ordered according to the `questionOrder` field.

Example Response : 

```json
[
    {
        "name": "Legal",
        "weight": 5,
        "questionOrder": "hits",
        "questions": [
            {
                "weight": 0,
                "topics": [
                    "594a917a01f55e000ff95b3d"
                ],
                "question": "Question 1",
                "answer" : "Answer 1",
                "hitCount" : 0,
                "date": "2017-06-29T12:00:29.120060",
                "_id": "594a924901f55e000ff95b3e",
                "isActive": true
            },
            {
                "weight": 0,
                "topics": [
                    "594a917a01f55e000ff95b3d"
                ],
                "question": "Question 2",
                "answer": "Answer 2",
                "hitCount": 0,
                "date": "2017-06-29T12:00:47.004486",
                "_id": "594a92a801f55e000ff95b3f",
                "isActive": true
            }
        ],
        "date": "2017-06-29T12:00:19.987768",
        "_id": "594a917a01f55e000ff95b3d",
        "description": "Information on Legal issues with questions and answers"
    }
]

```
-------------------------------

`POST /topic/toggle` switches the sorting order of a set of questions.

URL Params : `?order=hits|weight`

Example Body : 
```json
[
    "594a917a01f55e000ff95b3d",
    "594a917a01f55e000ff95b3e"
]
```

### Question

#### Structure
```json
{
    "question" : "str",
    "answer" : "str",
    "date" : "date",
    "isActive" : "bool",
    "weight" : "float",
    "hitCount" : "int",
    "topics" : ["topic_ids"]
}
```

Required : 
1. `question`
2. `answer`
3. `isActive`
4. `weight`
5. `hitCount`
6. `topics`

#### API

`GET /question` returns a list of all question embedded with their topics.

Example Response :

```json
[
    {
        "weight": 0,
        "topics": [
            {
                "name": "Legal",
                "weight": 5,
                "questionOrder": "hits",
                "date": "2017-06-29T12:00:19.987768",
                "_id": "594a917a01f55e000ff95b3d",
                "description": "Information on Legal issues with questions and answers"
            }
        ],
        "question": "Question 1",
        "answer" : "Answer 1",
        "hitCount": 0,
        "date": "2017-06-29T12:00:29.120060",
        "_id": "594a924901f55e000ff95b3e",
        "isActive": true
    },
    {
        "weight": 0,
        "topics": [
            {
                "name": "Legal",
                "weight": 5,
                "questionOrder": "hits",
                "date": "2017-06-29T12:00:19.987768",
                "_id": "594a917a01f55e000ff95b3d",
                "description": "Information on Legal issues with questions and answers"
            }
        ],
        "question": "Question 2",
        "answer": "Answer 2",
        "hitCount": 0,
        "date": "2017-06-29T12:00:47.004486",
        "_id": "594a92a801f55e000ff95b3f",
        "isActive": true
    }
]

```

--------------------------------------------

`GET /question/<id>` returns the question with the specified id.

Example `GET /question/594a924901f55e000ff95b3e`

```json
{
    "weight": 0,
    "topics": [
        {
            "name": "Legal",
            "weight": 5,
            "questionOrder": "hits",
            "date": "2017-06-29T12:00:19.987768",
            "_id": "594a917a01f55e000ff95b3d",
            "description": "Information on Legal issues with questions and answers"
        }
    ],
    "question": "Question 1",
    "answer" : "Answer 1",
    "hitCount": 0,
    "date": "2017-06-29T12:00:29.120060",
    "_id": "594a924901f55e000ff95b3e",
    "isActive": true
}
```

-------------------------------------------------
`POST /question` creates a new question or updates an existing one if the `_id` is supplied. The topic reference has to be referenced by it's id.

Example Body :

```json
{
    "weight": 0,
    "topics": [
        "594a917a01f55e000ff95b3d"
    ],
    "question": "Question 1",
    "answer" : "Answer 1",
    "hitCount": 0,
    "isActive": true
}
```
------------------------------------------------
`POST /question/toggle` changes the status of a set of questions.
URL Params : `?status=true|false`

Example Body : 
```json
[
    "594a917a01f55e000ff95b3d",
    "594a917a01f55e000ff95b3e"
]
```
--------------------------------------------------
`PUT /question/inc/<id>` increments the hitCount of a single question.

Exmample `PUT /question/inc/594a917a01f55e000ff95b3d`

--------------------------------------------------

`DELETE /question` deletes all questions.
--------------------------------------------------

`DELETE /question/<id>` deletes the question specified by the id.

Example : `DELETE /question/594a924901f55e000ff95b3e`

--------------------------------------------------

# Development

## Document Creation 

In order to create a new mongo document create a new file under the `documents` folder and the import it in the `main.py` application using python import expression and register it in the `mongoKit` framework.
Example :
```python
from documents import MyDocument

#...

mongo.register([MyDocument])
```

## Iterate documents 
As explained [in the MongoKit documentation](https://github.com/namlook/mongokit/wiki/Query)

## Create associations:

1. Embed the document inside another document which is not scalable.
2. Reference the document from another document.

## In order to return the referenced document simply query the database for that id and replace the id with the object.

Example taken from `topics` :
TODO : This query can be improved significantly by querying the database once. Or joining the two documents with the latest mongodb standard.

```python

def resolve_topics(question) :
	"""Resolve topics
	Modifies the argument and replaces the ids from the array 
	with the referenced topics.
	"""
    for i,item in enumerate(question.topics):
        question.topics[i] = mongo.Topic.find_one({"_id" : item})
    return question

@app.route('/question', methods=['GET'])
def get_all_questions():
	"""Returns all questions
	Iterates all questions from the database
	and modifies them to include the referenced topics.
	"""
    question = mongo.Question
    questions = [t for t in question.find()]
    [resolve_topics(question) for question in questions]
    return Response(json.dumps(questions,cls=ComplexEncoder),mimetype='application/json')

```