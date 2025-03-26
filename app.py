from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the database
db = SQLAlchemy(app)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(150), nullable=False)
    doctor_name = db.Column(db.String(150), nullable=False)
    appointment_type = db.Column(db.String(150), nullable=False)
    date = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book/<appointment_type>', methods=['GET', 'POST'])
def book_appointment(appointment_type):
    if request.method == 'POST':
        patient_name = request.form['patient_name']
        doctor_name = request.form['doctor_name']
        date = request.form['date']
        
        new_appointment = Appointment(patient_name=patient_name, doctor_name=doctor_name, 
                                      appointment_type=appointment_type, date=date)
        db.session.add(new_appointment)
        db.session.commit()

        flash(f'Appointment booked successfully with {doctor_name}!')
        return redirect(url_for('home'))
    return render_template('book.html', appointment_type=appointment_type)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json  # Expecting JSON data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')  # Store the password as plain text

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address already exists"}), 400

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful! You can now log in."}), 200

@app.route('/home')
def home():
    # if 'user_id' not in session:
    #     return redirect(url_for('index'))

    # user_id = session['user_id']
    # appointments = Appointment.query.filter_by(user_id=user_id).all()
    # return render_template('home.html', appointments=appointments)
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Expecting JSON data
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({"error": "Incorrect email or password"}), 400

    session['user_id'] = user.id  # Storing user ID in the session

    # Return URL to redirect to
    return jsonify({"message": "Login successful", "user_id": user.id, "username": user.username, "redirect_url": "/home"}), 200

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "You have been logged out."}), 200

if __name__ == '__main__':
    app.run(debug=True)
