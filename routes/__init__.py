from flask import Flask
from .index import index_bp
from .tire_strategy import tire_strategy_bp
from .colormap import colormap_bp
from .positions import positions_bp


def register_routes(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(tire_strategy_bp)
    app.register_blueprint(colormap_bp)
    app.register_blueprint(positions_bp)




