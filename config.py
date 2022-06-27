import datetime

class Configuration:
    DEBUG = True
    SECRET_KEY = "nn3200Mee"
    DATABASE = "/tmp/flsite.db"
    permanent_session_lifetime = datetime.timedelta(days=10)
    MAX_CONTENT_LENGTH = 1024 * 1024