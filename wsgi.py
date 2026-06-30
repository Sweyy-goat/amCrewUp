import pymysql
pymysql.install_as_MySQLdb()  # <-- Add these two lines at the very top

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app)