from ast import literal_eval

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy


DB = SQLAlchemy()

class Record(DB.Model):

  id = DB.Column(DB.BigInteger, primary_key=True)
  name = DB.Column(DB.String, nullable=False)
  age = DB.Column(DB.SmallInteger, nullable=False)

  def __repr__(self):
    """[Id: 0 | Name: James | Predicted Age: 27]"""
    return f'[Id: {self.id} | Name: {self.name} | Predicted Age: {self.age}]'


APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agify_data.sqlite3'
DB.init_app(APP)


@APP.route('/')
def base():
  return str(Record.query.all())


@APP.route('/no_older_than_40')
def filted_ages():
  filted = Record.query.filter(Record.age <= 40).all()
  return str(filted)


@APP.route('/check_name')
def check_name():
  BASE_URL = 'https://api.agify.io/?name='
  name = request.args['name']
  data = literal_eval(requests.get(BASE_URL + name).text)

  if not Record.query.all():  # returns []
    last_id = -1
  else:
    last_id = DB.session.query(DB.func.max(Record.id)).first()[0]

  try:
    rec = Record(id=last_id+1, name=data['name'], age=data['age'])
    DB.session.add(rec)
    DB.session.commit()
    return f'Record added: {rec}'
  except Exception as e:
    return str(e)


@APP.route('/refresh')
def refresh():
  DB.drop_all()
  DB.create_all()
  return 'Database Refreshed!'


if __name__ == '__main__':
  APP.run()