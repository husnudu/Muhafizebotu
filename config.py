from LaylaRobot.sample_config import Config

class Development(Config):
    OWNER_ID = 1799203251  # your telegram ID
    OWNER_USERNAME = "SpikerBey"  # your telegram username
    API_KEY = "1842730159:AAHDQDQvWTm6a4Mwvvj0NQfFdLnPVqaZPAE"  # your api key, as provided by the @botfather
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database'  # sample db credentials
    MESSAGE_DUMP = '-1234567890' # some group chat that your bot is a member of
    USE_MESSAGE_DUMP = True
    SUDO_USERS = [1816126399, 1108583389]  # List of id's for users which have sudo access to the bot.
    LOAD = []
    NO_LOAD = ['translation']
