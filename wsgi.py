import pymysql
pymysql.install_as_MySQLdb()

import eventlet
eventlet.monkey_patch() # <-- Move it to the absolute top line of wsgi.py

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)