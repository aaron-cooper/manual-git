from config import Config

# return a tuple (username, email)
def get_user_info(path_to_config: str) -> (str | None, str | None):
    config = Config.from_file(path_to_config)
    username = config.get('user', 'name')
    email = config.get('user', 'email')
    return (username, email)