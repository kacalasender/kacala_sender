import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.urls import unquote

app = Flask(__name__)
app.secret_key = 'magezaisnotakacalaman'
app.config['SESSION_TYPE'] = 'filesystem'  # You can choose a different session type if needed

# Define user credentials
users = {
    'mageza': 'Kigali$123',
    'kacala': 'Kicukiro$12'
}

def verify_password(username, password):
    if username in users and users[username] == password:
        return True
    return False

def send_email(smtp_server, port, sender_email, sender_name, password, message, contacts):
    try:
        success_messages = []  # Include success messages for each contact

        for contact in contacts:
            try:
                # Create a connection to the SMTP server
                server = smtplib.SMTP(smtp_server, port)
                server.starttls()

                # Login to the SMTP server
                server.login(sender_email, password)

                # Compose the email message
                msg = MIMEMultipart()
                msg['From'] = sender_name
                msg['To'] = contact
                msg['Subject'] = request.form['subject']  # Get the subject from the form
                msg.attach(MIMEText(message, 'html'))  

                # Send the email
                server.sendmail(sender_email, contact, msg.as_string())
                server.quit()

                # Add a success message for this contact
                success_messages.append(f"Email sent to {contact}")

            except Exception as e:
                # Add an error message for this contact
                success_messages.append(f"Error sending email to {contact}: {str(e)}")

        return success_messages
    except Exception as e:
        return [f"Error sending email: {str(e)}"]

@app.route('/')
def redirect_to_landing():
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if verify_password(username, password):
            session['user'] = username  # Store the logged-in user in the session
            return redirect(url_for('home'))
        else:
            flash('Incorrect login. Please try again.', 'error')  # Flash an error message
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contacts.html')

@app.route('/modify-contacts', methods=['POST'])
def modify_contacts():
    try:
        # Check if SMS gateway is specified
        sms_gateway = request.form.get('smsGateway', None)

        # Read uploaded contacts file (TXT)
        contacts_file = request.files['contactsFile']
        if not contacts_file:
            flash('Contacts file not provided.', 'error')
            return redirect(url_for('contacts_form'))

        contacts = []
        if contacts_file.filename.endswith('.txt'):
            # Process the contacts file
            for line in contacts_file.read().decode().splitlines():
                # Remove the "1" and add the SMS gateway domain
                modified_contact = line[1:] + sms_gateway
                contacts.append(modified_contact)

        if not contacts:
            flash('No valid contacts in the file.', 'error')
            return redirect(url_for('contacts_form'))

        # Save the modified contacts to a session variable
        session['contacts'] = contacts

        # Redirect to the email form (index.html) with a success message
        flash('Contacts have been modified.', 'success')
        return redirect(url_for('email_form'))
    except Exception as e:
        flash('Error modifying contacts: ' + str(e), 'error')
        return redirect(url_for('contacts_form'))

@app.route('/contacts-form')
def contacts_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contacts.html')

@app.route('/email-form', methods=['GET'])
def email_form():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email_route():
    if 'user' not in session:
        return redirect(url_for('login'))

    try:
        smtp_server = request.form['smtp']
        port = request.form['port']
        sender_email = request.form['senderEmail']
        sender_name = request.form['senderName']
        password = request.form['password']
        message = request.form['message']

        # Read the modified contacts from the session
        contacts = session.get('contacts', [])

        if not contacts:
            flash('No modified contacts available.', 'error')
            return redirect(url_for('email_form'))

        success_messages = send_email(smtp_server, port, sender_email, sender_name, password, message, contacts)

        for message in success_messages:
            flash(message, 'success')

        return redirect(url_for('email_form'))
    except Exception as e:
        flash('Error sending emails: ' + str(e), 'error')
        return redirect(url_for('email_form'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
