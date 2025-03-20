# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 10:50:23 2021

@author: Nupur Patel
"""

from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import pickle
import re
from PIL import Image
import numpy as np

# Keras
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime
import pytz
from fpdf import FPDF
from flask import send_file
from flask_mail import Mail, Message

#from gevent.pywsgi import WSGIServer

# Define a flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirects unauthorized users to login page
app.secret_key = 'secret_key'  # Required for session security(flash msgs)


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use Gmail's SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False 
app.config['MAIL_USERNAME'] = 'my.pulmonologist.prediction@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'bloc cnfq lqzo lyoh'  # Use App Password, not your actual password
app.config['MAIL_DEFAULT_SENDER'] = 'my.pulmonologist.prediction@gmail.com'

mail = Mail(app)  # Initialize Flask-Mail


# Model saved with Keras model.save()
MODEL_PATH ='multilungs_mobilenet_E40_ACC97_val85.h5'

# Load your trained model
model = load_model(MODEL_PATH)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True) # Email should be unique
    password = db.Column(db.String(100))
    predictions = db.relationship('Prediction', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user',lazy = True)  # Link to feedbacks

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  


# Feedback Model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming you have a User model
    feedback_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    
with app.app_context():
    db.create_all() # Creates all the tables

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('login'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)  # Log in the user after registration
        flash('Registration successful!', 'success')
        return redirect('/dashboard')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)  # Flask-Login handles session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')    

    return render_template('login.html')



@app.route('/dashboard')
@login_required  # Ensures only logged-in users can see their dashboard
def dashboard():
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.timestamp.desc()).all()

    # Convert timestamps to Eastern Time (Ohio)
    eastern_tz = pytz.timezone('America/New_York')  # Ohio is in the Eastern Time Zone

    # Convert backslashes to forward slashes before sending to template
    for prediction in predictions:
        prediction.image_path = prediction.image_path.replace("\\", "/")
        if prediction.timestamp:  # Ensure timestamp exists
            prediction.timestamp = prediction.timestamp.replace(tzinfo=pytz.utc).astimezone(eastern_tz)    
    
    
    return render_template('dashboard.html', user=current_user, predictions=predictions)
    
    # return redirect('/login')

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return render_template('index.html')


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   
  

    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="Benign"
    elif preds==1:
        preds="COVID"
    elif preds==2:
        preds="Malignant"
    elif preds==3:
        preds="Normal"
    elif preds==4:
        preds="Pneumonia"
    else:
        preds="TB"
    
    
    return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/predictnow', methods=['GET'])
def predictnow():
    # Main page
    return render_template('predict.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to static/uploads
        basepath = os.path.dirname(__file__)  # Get the base path of the application
        upload_folder = os.path.join(basepath, 'static/uploads')  # Define the correct upload path

        # Ensure the directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # Create if it doesn't exist

        file_path = os.path.join(upload_folder, secure_filename(f.filename))  # Save file in static/uploads
        f.save(file_path)
        
        # Make prediction
        preds = model_predict(file_path, model)
        result=preds
        # Save prediction result to database
        if current_user.is_authenticated:
            new_prediction = Prediction(user_id=current_user.id, image_path=file_path, result=result)
            db.session.add(new_prediction)
            db.session.commit()

        # flash('Prediction saved successfully!', 'success')
        return result
    
    return render_template("predict.html")
    

@app.route('/delete_prediction/<int:prediction_id>', methods=['POST'])
@login_required
def delete_prediction(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)
      

    # Ensure user is deleting only their own prediction
    if prediction.user_id != current_user.id:
        abort(403)  # Forbidden

    # Delete image from static/uploads
    file_path = os.path.join(os.path.dirname(__file__), 'static', prediction.image_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete from database
    db.session.delete(prediction)
    db.session.commit()

    # flash('Prediction deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download_image/<int:prediction_id>')
@login_required
def download_image(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)

    # Convert timestamp to Eastern Time (Ohio)
    eastern_tz = pytz.timezone('America/New_York')
    if prediction.timestamp:
        prediction.timestamp = prediction.timestamp.replace(tzinfo=pytz.utc).astimezone(eastern_tz)


    image_path = os.path.join("static", "uploads", os.path.basename(prediction.image_path))
    
    return send_file(image_path, as_attachment=True)


@app.route('/download_pdf/<int:prediction_id>')
@login_required
def download_pdf(prediction_id):
    prediction = Prediction.query.get_or_404(prediction_id)

    # Convert timestamp to Eastern Time (Ohio)
    eastern_tz = pytz.timezone('America/New_York')
    if prediction.timestamp:
        prediction.timestamp = prediction.timestamp.replace(tzinfo=pytz.utc).astimezone(eastern_tz)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    
    # Add title
    pdf.cell(200, 10, "Lung Disease Prediction Report", ln=True, align='C')
    pdf.ln(10)
    
    # Add prediction details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Prediction: {prediction.result}", ln=True)
    pdf.cell(200, 10, f"Date: {prediction.timestamp.strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)

    # Add image
    image_path = prediction.image_path  # Ensure correct path
    if os.path.exists(image_path):
        pdf.image(image_path, x=10, y=pdf.get_y(), w=100)  # Adjust position and size
        pdf.ln(60)  # Space after image
    
    
    # Save PDF
    pdf_path = f"static/reports/prediction_{prediction.id}.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

@app.route('/send_email', methods=['POST'])
@login_required
def send_email():
    recipient = request.form['email']
    prediction_id = request.form['prediction_id']

    prediction = Prediction.query.get_or_404(prediction_id)

    # Convert timestamp to Eastern Time (Ohio)
    eastern_tz = pytz.timezone('America/New_York')
    if prediction.timestamp:
        prediction.timestamp = prediction.timestamp.replace(tzinfo=pytz.utc).astimezone(eastern_tz)


    timestamp = prediction.timestamp.strftime('%Y-%m-%d %H:%M')

    subject = "Your Lung Disease Prediction Report"
    body = f"Hello,\n\nHere is your Lung disease prediction result.\n\nPrediction: {prediction.result}\nDate: {timestamp}\n\nPlease find the attached report and image."

    msg = Message(subject, recipients=[recipient], body=body)

    # Attach PDF report
    pdf = FPDF()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
 
    # Add title
    pdf.cell(200, 10, "Lung Disease Prediction Report", ln=True, align='C')
    pdf.ln(10)
 
    # Add prediction details
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Prediction: {prediction.result}", ln=True)
    pdf.cell(200, 10, f"Date: {prediction.timestamp.strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)
 
    # Add image
    image_path = prediction.image_path  # Ensure correct path
    if os.path.exists(image_path):
        pdf.image(image_path, x=10, y=pdf.get_y(), w=100)  # Adjust position and size
        pdf.ln(60)  # Space after image
 
 
    # Save PDF
    pdf_path = f"static/reports/prediction_{prediction.id}.pdf"
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as pdf:
            msg.attach(f"prediction_{prediction.id}.pdf", "application/pdf", pdf.read())

    # Attach Image
    image_path = prediction.image_path
    if os.path.exists(image_path):
        with open(image_path, 'rb') as img:
            msg.attach(os.path.basename(image_path), "image/jpeg", img.read())

    try:
        mail.send(msg)
        # flash('Email sent successfully!', 'success')
        print(f" Email sent successfully to {recipient}")
    except Exception as e:
        # flash(f'Error sending email: {str(e)}', 'danger')
        print(f" Error sending email: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    # Check if the form was submitted
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if the new password matches the confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('update_profile'))

        # Get the current user
        user = User.query.get(current_user.id)

        # Check if the email is already taken by another user
        if email != user.email and User.query.filter_by(email=email).first():
            flash('Email is already taken by another user.', 'danger')
            return redirect(url_for('update_profile'))

        # Update the user's details
        user.name = name
        user.email = email

        # If a new password is provided, update it
        if password:
            user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Commit the changes to the database
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_profile.html')

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    feedback_text = request.form['feedback_text']

    # Create new Feedback object and associate it with the logged-in user
    feedback = Feedback(user_id=current_user.id, feedback_text=feedback_text)
    
    # Add the feedback to the database and commit
    db.session.add(feedback)
    db.session.commit()

    flash('Feedback submitted successfully!', 'success')
    return redirect(url_for('dashboard'))  # Redirect to any page after submission, like the dashboard


    




if __name__ == '__main__':
    app.run(debug=True)
