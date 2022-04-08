from signal import Signals
from flaskr import create_app
from flask_restful import Api

from resources.homepage import Homepage
from resources.search import Search
from resources.auth import Login
from resources.auth import Signup
from resources.restaurant import Restaurant

import os

app = create_app()
api = Api(app)

api.add_resource(Homepage, '/')
api.add_resource(Search, '/search')
api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(Restaurant, '/restaurant')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9898))
    app.run(host='127.0.0.1', port=port, debug=True)
    app.secret_key()
