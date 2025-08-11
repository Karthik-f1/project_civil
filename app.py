import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# App setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
# SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site_data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

csrf = CSRFProtect(app)
db = SQLAlchemy(app)

# Models
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

# Forms
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

# Create DB if not exists
# @app.before_first_request
# def create_tables():
#     db.create_all()
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services', methods=['GET', 'POST'])
def services():
    form = ServiceInquiryForm()
    if form.validate_on_submit():
        inquiry = ServiceInquiry(
            company=form.company.data,
            contact_name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            service_type=form.service_type.data,
            project_details=form.project_details.data
        )
        db.session.add(inquiry)
        db.session.commit()
        app.logger.info(f'New service inquiry: {inquiry.id} {inquiry.company}')
        flash('Thank you for your inquiry — our team will contact you shortly.', 'success')
        return redirect(url_for('services'))
    return render_template('services.html', form=form)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        app.logger.info(f'New contact message: {contact.id} {contact.name}')
        flash('Thanks — we received your message and will reply soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

# Simple admin view to list submissions (for testing; remove in production)
@app.route('/admin/contacts')
def admin_contacts():
    contacts = Contact.query.order_by(Contact.submitted_at.desc()).all()
    return render_template('admin_contacts.html', contacts=contacts)

@app.route('/admin/inquiries')
def admin_inquiries():
    inquiries = ServiceInquiry.query.order_by(ServiceInquiry.submitted_at.desc()).all()
    return render_template('admin_inquiries.html', inquiries=inquiries)

if __name__ == '__main__':
    app.run(debug=True)