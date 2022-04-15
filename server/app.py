from signal import Signals
from flaskr import create_app
from flask_restful import Api

from resources.homepage import Homepage
from resources.search import Search
from resources.auth import Login
from resources.auth import Signup
from resources.restaurant import Restaurant
from resources.reservation import Reservation

import os

app = create_app()
api = Api(app)

api.add_resource(Homepage, '/')
api.add_resource(Search, '/search')
api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(Restaurant, '/restaurant/<int:restaurant_id>')
api.add_resource(Reservation, '/reservation/<int:restaurant_id>')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8111))
    app.run(host='0.0.0.0', port=port, debug=True)
    app.secret_key()
