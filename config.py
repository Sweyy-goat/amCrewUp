import os

class Config:
    # Railway automatically provides the MYSQL_URL variable if using a provisioned MySQL service
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYSQL_URL') or os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'super-secret-campus-key')
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 # 2MB Max profile picture upload