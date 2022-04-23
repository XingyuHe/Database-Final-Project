import os
from flask import Flask

def create_app():
    app = Flask(__name__,
                static_folder="../static", 
                instance_relative_config=True,
                template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY="peterhe-zhehua"
    )
    app.secret_key = os.urandom(12)

    return app