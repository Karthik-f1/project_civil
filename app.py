import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# ----------------- Models -----------------
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(300), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

class ServiceInquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(40), nullable=True)
    service_type = db.Column(db.String(80), nullable=False)
    project_details = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- Forms -----------------
class ContactForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)])

class ServiceInquiryForm(FlaskForm):
    company = StringField('Company Name', validators=[DataRequired(), Length(min=2, max=150)])
    name = StringField('Contact Person', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    phone = TelField('Phone Number', validators=[Optional(), Length(min=10, max=20)])
    service_type = SelectField('Service Type', choices=[
        ('structural_testing', 'Structural Load & Response Testing'),
        ('ndt_inspection', 'Non-Destructive Testing & Inspection'),
        ('geotechnical_testing', 'Geotechnical & Foundation Testing'),
        ('custom_solution', 'Custom Testing Solution'),
        ('equipment_rental', 'Equipment Rental'),
        ('training_certification', 'Training & Certification'),
        ('consultation', 'Engineering Consultation')
    ], validators=[DataRequired()])
    project_details = TextAreaField('Project Details', validators=[DataRequired(), Length(min=20, max=3000)])

with app.app_context():
    db.create_all()

# -------------- Catalog --------------
CATEGORIES = [
    {"slug": "load-testing", "name": "Load & Response Testers"},
    {"slug": "ndt-inspection", "name": "NDT & Inspection"},
    {"slug": "geotechnical", "name": "Geotechnical & Foundation"},
]

PRODUCTS = [
    {
        "slug": "bridge-load-test-kits",
        "title": "Bridge Load Test Kits",
        "category": "load-testing",
        "lead": "Proof-load and response measurement kits for bridges and heavy civil structures.",
        "bullets": [
            "Hydraulic jacks, calibrated load cells, and reaction frames",
            "Wireless DAQ with strain, displacement, and acceleration",
            "Live dashboards and PDF report templates",
            "ASTM/AASHTO workflow guidance"
        ],
        "specs": {
            "Max Load Capacity": "2,000 kN (modular)",
            "Displacement Range": "0–150 mm (LVDT)",
            "Sampling Rate": "Up to 2,000 Hz",
            "Ingress Protection": "IP67 sensors"
        },
        "hero": "/static/images/bridge_load_hero.png",
        "gallery": ["/static/images/bridge_load_1.png", "/static/images/bridge_load_2.png"]
    },
    {
        "slug": "ground-penetrating-radar",
        "title": "Ground Penetrating Radar (GPR)",
        "category": "ndt-inspection",
        "lead": "Subsurface imaging for rebar mapping, void detection, and cover depth analysis in concrete.",
        "bullets": [
            "Dual-frequency antennas for deep and shallow scans",
            "On-site heatmaps and 3D slices",
            "High-resolution concrete inspection",
            "CAD/BIM export formats"
        ],
        "specs": {
            "Depth Range": "Up to 60 cm (concrete)",
            "Antenna": "400/900 MHz",
            "Localization": "GNSS + wheel encoder",
            "Display": "10\" sunlight-readable"
        },
        "hero": "/static/images/gpr_hero.png",
        "gallery": ["/static/images/gpr_1.png"]
    },
    {
        "slug": "ultrasonic-pulse-velocity",
        "title": "Ultrasonic Pulse Velocity Tester",
        "category": "ndt-inspection",
        "lead": "Assess concrete quality, detect cracks, and evaluate uniformity using UPV measurement.",
        "bullets": [
            "Direct, semi-direct, and indirect modes",
            "Transit time and velocity computation",
            "Temperature compensation",
            "Data export for QA/QC reporting"
        ],
        "specs": {
            "Pulse Width": "0.1–10 µs",
            "Transducers": "54 / 82 / 150 kHz",
            "Range": "0.1–10,000 µs",
            "Memory": "10,000 readings"
        },
        "hero": "/static/images/upv_hero.png",
        "gallery": ["/static/images/upv_1.png"]
    },
    {
        "slug": "rebar-locator-covermeter",
        "title": "Rebar Locator & Covermeter",
        "category": "ndt-inspection",
        "lead": "Locate reinforcement, estimate bar size, and measure cover depth without destructive coring.",
        "bullets": [
            "Multi-sensor probe with auto-calibration",
            "Cover depth mapping with heatmap",
            "Bar size estimation (AASHTO guidance)",
            "Bluetooth data sync"
        ],
        "specs": {
            "Cover Range": "5–180 mm",
            "Bar Diameter Estimation": "10–40 mm (typical)",
            "Display": "5\" IPS",
            "Storage": "32 GB"
        },
        "hero": "/static/images/covermeter_hero.png",
        "gallery": ["/static/images/covermeter_1.png"]
    },
    {
        "slug": "plate-load-tester",
        "title": "Plate Load Tester",
        "category": "geotechnical",
        "lead": "On-site plate load testing for bearing capacity and modulus determination for foundations and subgrades.",
        "bullets": [
            "Modular reaction and jack kit",
            "Digital dial gauge/LVDT options",
            "Portable and ruggedized cases",
            "ASTM/IS code workflow templates"
        ],
        "specs": {
            "Plate Sizes": "300 / 450 / 600 mm",
            "Max Load": "1,000 kN (with proper reaction)",
            "Readout": "Digital/Analog",
            "Data": "CSV/PDF report"
        },
        "hero": "/static/images/plate_load_hero.png",
        "gallery": ["/static/images/plate_load_1.png"]
    },
]

def get_category(slug):
    return next((c for c in CATEGORIES if c["slug"] == slug), None)

def get_product(slug):
    return next((p for p in PRODUCTS if p["slug"] == slug), None)

# ----------------- Routes -----------------
@app.route('/')
def index():
    featured = PRODUCTS[:3]
    return render_template('index.html', categories=CATEGORIES, featured=featured)

@app.route('/catalog/<cat_slug>')
def catalog(cat_slug):
    cat = get_category(cat_slug)
    if not cat:
        return render_template('base.html', error_message="Category not found"), 404
    items = [p for p in PRODUCTS if p["category"] == cat_slug]
    return render_template('catalog.html', category=cat, items=items, categories=CATEGORIES)

@app.route('/product/<slug>')
def product_detail(slug):
    product = get_product(slug)
    if not product:
        return render_template('base.html', error_message="Product not found"), 404
    siblings = [p for p in PRODUCTS if p["category"] == product["category"] and p["slug"] != slug]
    cat = get_category(product["category"])
    return render_template(f'products/{slug}.html', product=product, category=cat, siblings=siblings, categories=CATEGORIES)

@app.route('/services', methods=['GET', 'POST'])
def services():
    form = ServiceInquiryForm()
    if form.validate_on_submit():
        entry = ServiceInquiry(
            company=form.company.data,
            contact_name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            service_type=form.service_type.data,
            project_details=form.project_details.data
        )
        db.session.add(entry)
        db.session.commit()
        flash('Thanks! Your service inquiry has been submitted.', 'success')
        return redirect(url_for('services'))
    return render_template('services.html', form=form, categories=CATEGORIES)

@app.route('/about')
def about():
    return render_template('about.html', categories=CATEGORIES)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        item = Contact(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(item)
        db.session.commit()
        flash('Thanks! Your message has been received.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form, categories=CATEGORIES)

@app.route('/admin/contacts')
def admin_contacts():
    rows = Contact.query.order_by(Contact.submitted_at.desc()).all()
    return render_template('admin_contacts.html', contacts=rows, categories=CATEGORIES)

@app.route('/admin/inquiries')
def admin_inquiries():
    rows = ServiceInquiry.query.order_by(ServiceInquiry.submitted_at.desc()).all()
    return render_template('admin_inquiries.html', inquiries=rows, categories=CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)