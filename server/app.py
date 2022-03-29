from flaskr import create_app
from flask_restful import Api

from resources.homepage import Homepage
from resources.search import Search

import os

app = create_app()
api = Api(app)

api.add_resource(Homepage, '/')
api.add_resource(Search, '/search')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9898))
    app.run(host='127.0.0.1', port=port, debug=True)
