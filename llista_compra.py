# La llista de la compra pels alumnes de DAW

from flask import Flask, request, jsonify
import uuid
import hashlib
from persistencia import Persistencia
import json

app = Flask(__name__)
persistencia = Persistencia()


@app.after_request
def apply_caching(response):
    response.headers["X-modul"] = "DAW2 Apps Hibrides"
    return response
           
@app.route('/articles/<int:article_id>',
           methods=['GET', 'PUT', 'DELETE'])
def article(article_id=0):
  valid_api_keys =persistencia.get_valid_api_keys()
  if not "x-api-key" in request.headers:
      return jsonify({"status": "error", "description": "Falta capçalera x-api-key"}), 401
  if valid_api_keys.get(request.headers['x-api-key'], None) is None:
      return jsonify({"status": "error", "description": "Credencials no vàlides"}), 401
  if request.method == 'GET':
    article = persistencia.get_article_by_id(article_id)
    if article is not None:
       return jsonify(article)
    return jsonify({}), 404
  elif request.method == 'DELETE':
    article = persistencia.remove_article_by_id(article_id)
    return jsonify({}), 204
  elif request.method == 'PUT':
    article = persistencia.update_article_by_id(article_id, request.json)
    return jsonify(article), 200


@app.route('/articles', methods=['GET', 'POST'])
def get_articles():
  valid_api_keys =persistencia.get_valid_api_keys()
  if not "x-api-key" in request.headers:
      return jsonify({"status": "error", "description": "Falta capçalera x-api-key"}), 401
  if valid_api_keys.get(request.headers['x-api-key'], None) is None:
      return jsonify({"status": "error", "description": "Credencials no vàlides"}), 401
  if request.method == 'GET':
    return jsonify(persistencia.get_articles())
  elif request.method == 'POST':
    article = {
        'nom': request.json['nom'],
        'quantitat': request.json['quantitat']
    }
    article = persistencia.insert_article(article)
    if article is None:
       return jsonify({}), 400
    return jsonify(article), 201

@app.route('/login', methods=['POST'])
def login():
  valid_api_keys =persistencia.get_valid_api_keys()
  if not "authorization" in request.headers:
          return "", 401
  auth = request.authorization
  usuari = auth.usernamekey
  paraula_pas = auth.password
  usuari = persistencia.get_usuari_by_nom(usuari)
  if not usuari:
     return jsonify({}), 404
  if usuari["pwd"] == hashlib.sha256(paraula_pas.encode()).hexdigest():
    nova_api_key = uuid.uuid4().hex
    persistencia.add_api_key(nova_api_key, usuari)
    valid_api_keys = persistencia.get_valid_api_keys()
    return jsonify({'resultat': 'success', 'x-api-key': nova_api_key})
  return jsonify({'resultat': 'error', 'user':usuari, 'pwd': paraula_pas}), 401

if __name__ == "__main__":
  app.run()
