#!/usr/bin/python3

import mysql.connector, json
class Persistencia():

    def __init__(self):
        self.open_conn()

    def open_conn(self):
        ruta_codi = "/home/xaviq/mysite/"
        with open(f"{ruta_codi}env.json") as conf:
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
        except mysql.connector.errors.ProgrammingError:
            return False
        return True

    def create_tables(self):
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def get_article_by_id(self, article_id):
        if not self.conn._open_connection:
            self.open_conn()
        query = "Select * from articles where id=%s";
        cursor = self.conn.cursor();
        cursor.execute(query, (article_id,))
        article = cursor.fetchone()

