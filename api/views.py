from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError

import status
from models import Category, CategorySchema, Message, MessageSchema, db

api_bp = Blueprint('api', __name__)
category_schema = CategorySchema()
message_schema = MessageSchema()
api = Api(api_bp)


class MessageResource(Resource):
    def get(self, id):
        message = Message.query.get_or_404(id)
        result = message_schema.dump(message).data
        return result

    def patch(self, id):
        message = Message.query.get_or_404(id)
        message_dict = request.get_json(force=True)
        if 'message' in message_dict:
            message.message = message_dict['message']
        if 'duration' in message_dict:
            message.duration = message_dict['duration']
        if 'printed_times' in message_dict:
            message.printed_times = message_dict['printed_times']
        if 'printed_once' in message_dict:
            message.printed_once = message_dict['printed_once']
        dumped_message, dump_errors = messsage_schema.dump(message)
        if dump_errors:
            return dump_errors, status.HTTP_400_BAD_REQUEST
        validate_errors = message_schema.validate(dumped_message)
        #errors = message_schema.validate(data)
        if validate_errors:
            return validate_errors, status.HTTP_400_BAD_REQUEST
        try:
            message.update()
            return self.get(id)
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST

    def delete(self, id):
        message = Message.query.get_or_404(id)
        try:
            delete = Message.delete(message)
            response = make_response()
            return response, status.HTTP_204_NO_CONTENT
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_401_UNAUTHORIZED


class MessageListResource(Resource):
    def get(self):
        messages = Message.query.all()
        result = message_schema.dump(messages, many=True).data
        return result

    def post(self):
        request_dict = request.get_json()
        if not request_dict:
            response = {"message": "No input data provided"}
            return response, status.HTTP_400_BAD_REQUEST
        errors = message_schema.validate(request_dict)
        if errors:
            return errors, status.HTTP_400_BAD_REQUEST
        try:
            category_name = request_dict['category']['name']
            category = Category.query.filter_by(name=category_name).first()
            if category is None:
                # Create a new category
                category = Category(name=category_name)
                db.session.add(category)
            # Create a new message
            message = Message(
                message=request_dict['message']
                duration=request_dict['duration']
                category=category
            )
            message.add(message)
            query = Message.query.get(message.id)
            result = message_schema.dump(query).data
            return result, status.HTTP_201_CREATED
        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            return resp, status.HTTP_400_BAD_REQUEST
