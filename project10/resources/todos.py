from flask import Blueprint

from flask_restful import (Resource, Api, reqparse,
                               inputs, fields, marshal,
                               marshal_with, url_for)

import models


todo_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                for todo in models.Todo.select()]
        return todos

    @marshal_with(todo_fields)
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return todo, 201, {
            'Location':url_for('resources.todos.todos')
        }

class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        todo = models.Todo.get(models.Todo.id == id)
        return todo

    @marshal_with(todo_fields)
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            todo = models.Todo.select().where(
                models.Todo.id == id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That todo does not exist or is not editable.'}
            ), 403)
        query = todo.update(**args)
        query.execute()
        return (models.Todo.get(models.Todo.id == id), 200,
                {'Location': url_for('resources.todos.todo', id=id)})

    def delete(self, id):
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint = 'todos'
)
api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)