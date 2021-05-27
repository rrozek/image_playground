import environ
import os


def _get_env() -> environ.Env:
    environment = environ.Env()

    # .env file, should load only in development environment
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        environ.Env.read_env(str(env_file))
    return environment


env = _get_env()
