import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.craftsman import Craftsman, CraftsmanService, PortfolioItem, Review
from src.routes.user import user_bp
from src.routes.craftsman import craftsman_bp
from src.routes.auth import auth_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(craftsman_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables and seed data
with app.app_context():
    db.create_all()
    
    # Seed some sample data if database is empty
    if Craftsman.query.count() == 0:
        sample_craftsmen = [
            Craftsman(
                name='محمد أحمد',
                email='mohamed.ahmed@email.com',
                phone='0658-125-4667',
                service_type='سباكة',
                location='الدار البيضاء - المعاريف',
                description='خبرة 15 سنة في أعمال السباكة وإصلاح التسريبات',
                experience_years=15,
                rating=4.8,
                reviews_count=24,
                completed_jobs=156,
                price_range='150-300 درهم',
                availability='متاح من السبت إلى الخميس، 8:00 ص - 6:00 م',
                is_verified=True
            ),
            Craftsman(
                name='علي حسين',
                email='ali.hussein@email.com',
                phone='0668-128-3547',
                service_type='كهرباء',
                location='الدار البيضاء - سيدي مومن',
                description='متخصص في التركيبات الكهربائية وإصلاح الأعطال',
                experience_years=12,
                rating=4.6,
                reviews_count=18,
                completed_jobs=89,
                price_range='200-400 درهم',
                availability='متاح يومياً من 9:00 ص - 7:00 م',
                is_verified=True
            ),
            Craftsman(
                name='سعيد علي',
                email='said.ali@email.com',
                phone='0665-125-4547',
                service_type='نجارة',
                location='الدار البيضاء - الحي المحمدي',
                description='صناعة وإصلاح الأثاث الخشبي والديكورات',
                experience_years=18,
                rating=4.9,
                reviews_count=31,
                completed_jobs=203,
                price_range='300-600 درهم',
                availability='متاح من الاثنين إلى السبت، 8:00 ص - 5:00 م',
                is_verified=True
            ),
            Craftsman(
                name='أحمد عبدالله',
                email='ahmed.abdullah@email.com',
                phone='0668-128-4547',
                service_type='صباغة',
                location='الدار البيضاء - عين السبع',
                description='طلاء الجدران والأسقف بأحدث التقنيات',
                experience_years=8,
                rating=4.4,
                reviews_count=12,
                completed_jobs=67,
                price_range='100-250 درهم',
                availability='متاح من الأحد إلى الجمعة، 7:00 ص - 4:00 م',
                is_verified=True
            )
        ]
        
        for craftsman in sample_craftsmen:
            db.session.add(craftsman)
        
        db.session.commit()
        print("Sample data seeded successfully!")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# API health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        'success': True,
        'message': 'API is running',
        'version': '1.0.0'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
