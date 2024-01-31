#!/usr/bin/python3

import mysql.connector, json, os
class Persistencia():

    def __init__(self):
        self.open_conn()

    def open_conn(self):

        ruta_codi = "/home/xaviq/mysite/"
        my_dir = os.path.dirname(__file__)
        ruta_config = os.path.join(my_dir, "env.json")
        with open(ruta_config) as conf:
            self.env = json.load(conf)
        self.conn = mysql.connector.connect(
                host=self.env['db_host'],
                user=self.env['db_user'],
                password=self.env['db_pwd'],
                database=self.env['db_name']
                )
        if not self.check_tables():
            self.create_tables()

    def check_tables(self):
        try:
            cursor = self.conn.cursor(buffered=True)
            cursor.execute("SELECT * FROM articles;")
            cursor.reset()
            cursor.execute("SELECT * FROM usuaris;")
            cursor.reset()
            cursor.execute("SELECT * FROM api_keys;")
            cursor.reset()
            cursor.execute("SELECT * FROM usuaris;")
            cursor.reset()
        except mysql.connector.errors.ProgrammingError:
            return False
        return True

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("Drop table if exists articles;")
        cursor.execute("Drop table if exists usuaris;")
        cursor.execute("Drop table if exists api_keys;")
        cursor.execute("Drop table if exists usuaris;")

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
                        pwd char(64) not null,
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
        self.conn.commit()

    def get_article_by_id(self, article_id):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select id, nom, quantitat from articles where id=%s";
        cursor = self.conn.cursor();
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()
        if not article:
            return None
        return {
            'id': article[0],
            'nom': article[1],
            'quantitat': article[2]
            }
    
    def get_article_by_nom(self, article_nom):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select id, nom, quantitat from articles where nom=%s";
        cursor = self.conn.cursor();
        cursor.execute(query, (article_nom,))
        article = cursor.fetchone()
        if not article:
            return None
        return {
            'id': article[0],
            'nom': article[1],
            'quantitat': article[2]
            }
    
    def get_articles(self):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select id, nom, quantitat from articles";
        cursor = self.conn.cursor();
        cursor.execute(query)
        result_query = cursor.fetchall()
        articles = []
        for article in result_query:
            articles.append({
            'id': article[0],
            'nom': article[1],
            'quantitat': article[2]
            })
        return  articles
    
    def remove_article_by_id(self, article_id):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Delete from articles where id=%s;"
        cursor = self.conn.cursor()
        cursor.execute(query, (article_id,))
        self.conn.commit()
        return True
    
    def insert_article(self, article):
        if not self.conn._open_connection:
            self.open_conn()
        query = "insert into articles (nom, quantitat) values(%s, %s);"
        cursor = self.conn.cursor();
        try:
            cursor.execute(query, (article["nom"], article["quantitat"]))
        except BaseException as be:
            return None
        self.conn.commit()

        return self.get_article_by_id(cursor.lastrowid)
    
    def update_article_by_id(self, id, article):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Update articles set nom=%s, quantitat=%s where id=%s"
        cursor = self.conn.cursor()
        cursor.execute(query, (article["nom"], article["quantitat"], id))
        self.conn.commit()
        return self.get_article_by_id(id)

    
    def get_usuari_by_nom(self, usuari_nom):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select id, nom, pwd from usuaris where nom=%s";
        cursor = self.conn.cursor();
        cursor.execute(query, (usuari_nom,))
        usuari = cursor.fetchone()
        if not usuari:
            return None
        return {"id":usuari[0],"nom":usuari[1],"pwd":usuari[2]}
    
    def get_valid_api_keys(self):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select usuari, api_key, data_creacio from api_keys;"
        cursor = self.conn.cursor()
        cursor.execute(query)
        api_keys = {}
        for api_key in cursor.fetchall():
            api_keys[api_key[1]]= {"user": api_key[0]}
        return api_keys
    
    def add_api_key(self, key, usuari):
        if not self.conn._open_connection:
            self.open_conn()
        query = "insert into api_keys (usuari, api_key) values(%s, %s);"
        cursor = self.conn.cursor();
        try:
            cursor.execute(query, ( usuari["id"], key))
        except BaseException as be:
            return None
        self.conn.commit()

        return self.get_article_by_id(cursor.lastrowid)



    
if __name__ == "__main__":
    p = Persistencia()
    article = p.get_article_by_nom('tonyina')
    if (article):
        print(p.get_article_by_id(article["id"]))
        print(p.remove_article_by_id(article["id"]))
    print(p.insert_article({"nom": "tonyina", "quantitat": 4}))