from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 🔧 Flask & DB Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/demodb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 🧱 Resource Table Model
class Resource(db.Model):
    __tablename__ = 'resources'  # Explicitly define the table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    subject = db.Column(db.Text)
    semester = db.Column(db.Text)
    department = db.Column(db.Text)
    type = db.Column(db.Text)
    source = db.Column(db.Text)
    link = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ Health check route
@app.route("/")
def home():
    return "✅ TechIT ResourceHub API is running!"

# 🔍 Simple search endpoint
@app.route("/search")
def search():
    query = request.args.get("q", "").lower()
    results = Resource.query.filter(Resource.title.ilike(f"%{query}%")).limit(20).all()
    return jsonify([
        {
            "title": r.title,
            "subject": r.subject,
            "semester": r.semester,
            "department": r.department,
            "type": r.type,
            "source": r.source,
            "link": r.link
        } for r in results
    ])

# (Optional) ➕ Test insert via HTTP POST (for testing only)
@app.route("/add", methods=["POST"])
def add_resource():
    data = request.get_json()
    try:
        resource = Resource(
            title=data["title"],
            subject=data["subject"],
            semester=data["semester"],
            department=data["department"],
            type=data["type"],
            source=data["source"],
            link=data["link"]
        )
        db.session.add(resource)
        db.session.commit()
        return jsonify({"message": "✅ Resource added!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 🚀 Launch the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        try:
            # Connection check
            count = db.session.query(Resource).count()
            print(f"✅ Connected to DB. {count} resource(s) found.")
        except Exception as e:
            print("❌ Error connecting to DB:", e)

    app.run(debug=True)
