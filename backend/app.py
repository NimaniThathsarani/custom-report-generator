from flask import Flask
from flask_cors import CORS
from backend.routes.report_routes import report_bp

def create_app():
    app = Flask(__name__)
    
    # Enable Cross-Origin Resource Sharing (CORS) so Frontend groups can call this API smoothly
    CORS(app)

    # Register application blueprints/routes
    app.register_blueprint(report_bp)

    @app.route('/')
    def index():
        return {"message": "Custom Report Generator Backend Engine is running smoothly!"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)