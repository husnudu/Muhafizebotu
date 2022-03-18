from LaylaRobot.sample_config import Config

class Development(Config):
    OWNER_ID = 5200193996  # your telegram ID
    OWNER_USERNAME = "slmmnhusnu"  # your telegram username
    API_KEY = "5118244333:AAEF80E3lszb2hVLkl4mZ1gVEkP9aPPKmaI"  # your api key, as provided by the @botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database'  # sample db credentials
    MESSAGE_DUMP = '-407527950' # some group chat that your bot is a member of
    USE_MESSAGE_DUMP = True
    SUDO_USERS = [5283911733]  # List of id's for users which have sudo access to the bot.
    LOAD = []
    NO_LOAD = ['translation']
