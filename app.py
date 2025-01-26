import matplotlib
matplotlib.use('Agg')  # Use Agg backend for non-GUI rendering
from flask import Flask
from routes import register_routes  # Import the function to register routes

# Initialize the Flask application

app = Flask(__name__)


# Register the routes from the routes module
register_routes(app)


# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)