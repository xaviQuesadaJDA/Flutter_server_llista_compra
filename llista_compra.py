# La llista de la compra pels alumnes de DAW

from flask import Flask, request, jsonify
import uuid
import hashlib
import mysql.connector

app = Flask(__name__)


articles = []
last_id = 0

users = {'obret':hashlib.sha256(b"sesam").hexdigest(), 'xavi':hashlib.sha256(b"1234").hexdigest()}
def check_tables():
  try:
      cursor = conn.cursor(buffered=True)
      cursor.execute("SELECT * FROM articles;")
      cursor.reset()
      cursor.execute("SELECT * FROM usuaris;")
      cursor.reset()
      cursor.execute("SELECT * FROM api_keys;")
      cursor.reset()
  except mysql.connector.errors.ProgrammingError:
      return False
  return True

def create_tables():
  cursor = conn.cursor()
  cursor.execute("Drop table if exists articles;")
  cursor.execute("Drop table if exists usuaris;")
  cursor.execute("Drop table if exists api_keys;")
  
  cursor.execute("""
              Create table if not exists articles(
                id int not null auto_increment,
                nom varchar(255) unique,
                quantitat int not null,
                primary key (id)
              )
                """)
  cursor.execute("""
              Create table if not exists usuaris(
                id int not null auto_increment,
                nom varchar(255) unique,
                password char(64) not null,
                primary key (id)
              )
                """)
  cursor.execute("""
              Create table if not exists api_keys(
                id int not null auto_increment,
                usuari int not null references usuaris(id),
                api_key varchar(100),
                data_creacio DATETIME DEFAULT CURRENT_TIMESTAMP,
                primary key (id)
              )
                """)
  conn.commit()

conn = mysql.connector.connect(
                host='localhost',
                user='xaviq',
                password='MTIzNA==',
                database='xaviq$default'
                )
if not check_tables():
    create_tables()
    
@app.route('/articles/<int:article_id>',
           methods=['GET', 'PUT', 'DELETE'])
def article(article_id=0):
  global last_id
  global articles
  if request.method == 'GET':
    trobat = [art for art in articles if art["id"] == article_id]
    if len(trobat) > 0:
      return jsonify(trobat[0])
    return jsonify({}), 404
  elif request.method == 'DELETE':
    trobat = [art for art in articles if art["id"] == article_id]
    if len(trobat) > 0:
      articles.remove(trobat[0])
    return jsonify({}), 204
  elif request.method == 'PUT':
    for index, value in enumerate(articles):
      if value["id"] == article_id:
        articles[index] = request.json
        return jsonify(articles[index]), 200


@app.route('/articles', methods=['GET', 'POST'])
def get_articles():
  global articles
  global last_id
  if request.method == 'GET':
    return jsonify(articles)
  elif request.method == 'POST':
    last_id +=1
    article = {
        'id': last_id,
        'nom': request.json['nom'],
        'quantitat': request.json['quantitat']
    }
    articles.append(article)
    return jsonify(article), 201
  
@app.route('/login', methods=['POST'])
def login():
  if not "authorization" in request.headers:
          return "", 401
  auth = request.authorization
  usuari = auth.username
  paraula_pas = auth.password
  if users.get(usuari, None) == hashlib.sha256(paraula_pas.encode()).hexdigest():
    return jsonify({'resultat': 'success', 'x-api-key': uuid.uuid4().hex})
  return jsonify({'resultat': 'error', 'user':usuari, 'pwd': paraula_pas}), 401

if __name__=="__main__":
  app.run(host='0.0.0.0')