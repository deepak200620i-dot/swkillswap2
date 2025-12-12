from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_mail import Mail
from config import config
from routes import auth_bp, profile_bp, skills_bp, matching_bp, requests_bp, reviews_bp, chat_bp

# Initialize Flask-Mail
mail = Mail()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    from database import init_db
    with app.app_context():
        init_db()

    app.config.from_object(config[config_name])
    # Initialize DB on start (only if tables do not exist)
    from database import init_db

    with app.app_context():
        try:
            init_db()
        except Exception as e:
            app.logger.error(f"DB init error: {e}")
    
    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(matching_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(reviews_bp)

    app.register_blueprint(chat_bp)

    from routes.notifications import notifications_bp
    app.register_blueprint(notifications_bp)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}")
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return e

        # non-HTTP exceptions only
        app.logger.error(f"Unhandled Exception: {e}", exc_info=True)

        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500
        return render_template('errors/500.html'), 500

    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Auth routes (templates)
    @app.route('/login')
    def login_page():
        return render_template('auth/login.html')

    @app.route('/signup')
    def signup_page():
        return render_template('auth/signup.html')

    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard/user_dashboard.html')

    # Profile routes
    @app.route('/profile/<int:user_id>')
    def view_profile(user_id):
        return render_template('profile/view.html')

    @app.route('/profile/edit')
    def edit_profile():
        return render_template('profile/edit.html')

    # Skills routes
    @app.route('/skills')
    def browse_skills():
        return render_template('skills/browse.html')

    @app.route('/skills/search')
    def search_skills():
        return render_template('skills/search.html')

    # Matching route
    @app.route('/matching')
    def matching():
        return render_template('matching/matches.html')

    # Requests routes
    @app.route('/requests')
    def view_requests():
        return render_template('requests/list.html')

    # Reviews routes
    @app.route('/reviews/add')
    def add_review():
        return render_template('reviews/add.html')

    # Chat route
    @app.route('/chat')
    def chat_page():
        return render_template('chat/index.html')

    return app
# Global app instance for Gunicorn
app = create_app("production")

if __name__ == "__main__":
    from database import init_db

    try:
        init_db()
    except:
        pass

    import logging
    import sys

    logging.basicConfig(...)

    app.logger.info("Starting application...")
    app.run(debug=True, host="0.0.0.0", port=5000)
