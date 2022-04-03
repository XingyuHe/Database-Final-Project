import os
from flask import Flask

def create_app():
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder="../templates")
    app.config.from_mapping(
        SECRET_KEY="peterhe-zhehua"
    )

    return app