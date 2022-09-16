import sys
from flask_restful import reqparse, inputs, Resource, Api
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from marshmallow import Schema, fields
import datetime


app = Flask("app")
api = Api(app)
# part 3
engine = create_engine('sqlite:///Events.db', echo=True)
Session = sessionmaker(bind=engine)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///Events.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# создание таблицы и привязка ее к классу
class Events(db.Model):
    __tablename__ = "Events"
    id = Column(Integer, primary_key=True)
    event = Column(String(50))
    date = Column(Date)


db.create_all()


class Requests(Resource):
    def post(self):
        session = Session()  # SqlAlchemy :: Starts a session
        parser_post = reqparse.RequestParser()
        parser_post.add_argument('event', type=str,
                                 help="The event name is required!", required=True)
        parser_post.add_argument('date', type=inputs.date,
                                 help="The event date with the correct format is required!"
                                      " The correct format is YYYY-MM-DD!", required=True)
        args_post = parser_post.parse_args()
        session.add(Events(event=args_post["event"], date=args_post["date"].date()))
        session.commit()
        args_post["message"] = "The event has been added!"
        schema = MySchema()
        session.close()
        return schema.dump(args_post)

    def get(self, message=None):
        session = Session()  # SqlAlchemy :: Starts a session
        parser_get = reqparse.RequestParser()
        parser_get.add_argument('start_time', type=inputs.date, required=True)
        parser_get.add_argument('end_time', type=inputs.date, required=True)
        query = session.query(Events)
        schema = MySchema()
        all_rows = []
        try:
            args_get = parser_get.parse_args()
            all_rows = query.filter(Events.date.between(args_get["start_time"], args_get["end_time"])).all()
        except:
            if message is not None:
                if message.isdigit():
                    row = query.filter(Events.id == int(message)).first()
                    if row is not None:
                        session.close()
                        return schema.dump(row)
                    else:
                        session.close()
                        abort(404, "The event doesn't exist!")
                elif message == "today":
                    all_rows = query.filter(Events.date == datetime.date.today()).all()
                else:
                    all_rows = []
            else:
                all_rows = query.all()
        session.close()
        return [schema.dump(row) for row in all_rows]

    def delete(self, message=None):
        session = Session()  # SqlAlchemy :: Starts a session
        query = session.query(Events)
        schema = MySchema()
        event = query.filter(Events.id == message).first()
        print(event)
        if event is None:
            session.close()
            abort(404, "The event doesn't exist!")
        query.filter(Events.id == event.id).delete()
        session.commit()
        args = {"message": "The event has been deleted!"}
        session.close()
        return schema.dump(args)


class MySchema(Schema):
    id = fields.Integer()
    message = fields.String()
    event = fields.String()
    date = fields.Date()

api.add_resource(Requests, '/event/<message>', '/event', methods=["POST", "GET", "DELETE"])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
