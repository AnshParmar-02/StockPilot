from flask import Flask;

def create_app():
    app = Flask(__name__)

    #from app.routes import api imports the API Blueprint from another Python module.
    from app.routes import api
    app.register_blueprint(api)   #app.register_blueprint(api) connects those routes to the application

    #This pattern is called the Application Factory Pattern. It makes it easier to create different application instances for development and automated tests

    return app