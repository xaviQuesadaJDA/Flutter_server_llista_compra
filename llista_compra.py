# La llista de la compra pels alumnes de DAW

from flask import Flask, request, jsonify
import uuid
import hashlib
app = Flask(__name__)


articles = []
last_id = 0

users = {'obret':hashlib.sha256(b"sesam").hexdigest(), 'xavi':hashlib.sha256(b"1234").hexdigest()}
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