
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from mysql.connector import MySQLConnection
# import yaml
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'flashapp_secret_key'

config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "port": 3307,
    "database": "flashapp",
    "charset": "utf8mb4",
    "collation":"utf8mb4_general_ci"
}
cnx=MySQLConnection(**config)
app.secret_key='flashapp'


def is_logged_in():
    return 'user_id' in session

def get_user_decks(user_id):
    cursor = cnx.cursor()
    try:
        cursor.execute("SELECT * FROM decks WHERE user_id = %s ORDER BY last_studied DESC", [user_id])
        decks = cursor.fetchall()
    finally:
        cursor.close()
    return decks

def get_deck_cards(deck_id):
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM cards WHERE deck_id = %s", [deck_id])
    cards = cursor.fetchall()
    cursor.close()
    return cards

# Routes
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form fields
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        # Validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Please enter a valid email address', 'danger')
            return render_template('register.html')
        
        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        
        # Check if username or email already exists
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", [username, email])
        user = cursor.fetchone()
        
        if user:
            flash('Username or email already exists', 'danger')
            cursor.close()
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert new user
        cursor.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)", 
                   (username, email, hashed_password))
        cnx.commit()
        cursor.close()
        
        flash('Registration successful! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", [username])
        user = cursor.fetchone()

        if user:
            password = user[3]  # Assuming password is at index 3

            if check_password_hash(password, password_candidate):
                # Create session variables
                session['logged_in'] = True
                session['user_id'] = user[0]  # Assuming ID is at index 0
                session['username'] = username

                flash('Login successful!', 'success')
                cursor.close()
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid password', 'danger')
                cursor.close()
                return render_template('login.html')
        else:
            flash('Username not found', 'danger')
            cursor.close()
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    decks = get_user_decks(session['user_id'])
    return render_template('dashboard.html', decks=decks)

@app.route('/create_deck', methods=['GET', 'POST'])
def create_deck():
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO decks(name, description, user_id) VALUES(%s, %s, %s)", 
                   (name, description, session['user_id']))
        cnx.commit()
        deck_id = cursor.lastrowid
        cursor.close()
        
        flash('Deck created successfully!', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))
    
    return render_template('create_deck.html')

@app.route('/deck/<int:deck_id>')
def view_deck(deck_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Get deck info
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                        [deck_id, session['user_id']])
    
    deck = cursor.fetchone()
    if not deck:
        flash('Deck not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get cards in deck
    cards = get_deck_cards(deck_id)
    
    cursor.close()
    
    return render_template('view_deck.html', deck=deck, cards=cards)

@app.route('/deck/<int:deck_id>/edit', methods=['GET', 'POST'])
def edit_deck(deck_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if deck exists and belongs to user
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                        [deck_id, session['user_id']])
    
    deck = cursor.fetchone()
    if not deck:
        flash('Deck not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        cursor.execute("UPDATE decks SET name = %s, description = %s WHERE id = %s", 
                   (name, description, deck_id))
        cnx.commit()
        cursor.close()
        
        flash('Deck updated successfully!', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))
    
    cursor.close()
    return render_template('edit_deck.html', deck=deck)

@app.route('/deck/<int:deck_id>/delete', methods=['POST'])
def delete_deck(deck_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    cursor = cnx.cursor()
    # Check if deck exists and belongs to user
    result = cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                        [deck_id, session['user_id']])
    
    if result == 0:
        flash('Deck not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    # Delete the deck and all its cards
    cursor.execute("DELETE FROM cards WHERE deck_id = %s", [deck_id])
    cursor.execute("DELETE FROM decks WHERE id = %s", [deck_id])
    cnx.commit()
    cursor.close()
    
    flash('Deck deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/deck/<int:deck_id>/add_card', methods=['GET', 'POST'])
def add_card(deck_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Check if deck exists and belongs to user
    cursor = cnx.cursor()
    result = cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                        [deck_id, session['user_id']])
    
    if result == 0:
        flash('Deck not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    deck = cursor.fetchone()
    
    if request.method == 'POST':
        front = request.form['front']
        back = request.form['back']
        
        cursor.execute("INSERT INTO cards(front, back, deck_id) VALUES(%s, %s, %s)", 
                   (front, back, deck_id))
        cnx.commit()
        cursor.close()
        
        flash('Card added successfully!', 'success')
        return redirect(url_for('view_deck', deck_id=deck_id))
    
    cursor.close()
    return render_template('add_card.html', deck=deck)

@app.route('/card/<int:card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Get card details
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT c.*, d.user_id 
        FROM cards c 
        JOIN decks d ON c.deck_id = d.id 
        WHERE c.id = %s
    """, [card_id])
    card = cursor.fetchone()
    
    if not card or card[4] != session['user_id']:  # Assuming user_id is at index 4
        flash('Card not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        front = request.form['front']
        back = request.form['back']
        
        cursor.execute("UPDATE cards SET front = %s, back = %s WHERE id = %s", 
                   (front, back, card_id))
        cnx.commit()
        
        flash('Card updated successfully!', 'success')
        return redirect(url_for('view_deck', deck_id=card[3]))  # Assuming deck_id is at index 3
    
    cursor.close()
    return render_template('edit_card.html', card=card)

@app.route('/card/<int:card_id>/delete', methods=['POST'])
def delete_card(card_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    # Get card details
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT c.*, d.user_id 
        FROM cards c 
        JOIN decks d ON c.deck_id = d.id 
        WHERE c.id = %s
    """, [card_id])
    card = cursor.fetchone()
    
    if not card or card[4] != session['user_id']:  # Assuming user_id is at index 4
        flash('Card not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))
    
    deck_id = card[3]  # Assuming deck_id is at index 3
    
    cursor.execute("DELETE FROM cards WHERE id = %s", [card_id])
    cnx.commit()
    cursor.close()
    
    flash('Card deleted successfully!', 'success')
    return redirect(url_for('view_deck', deck_id=deck_id))

@app.route('/deck/<int:deck_id>/study')
def study(deck_id):
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

    cursor = cnx.cursor(dictionary=True)

    # Check if the deck exists and belongs to the logged-in user
    cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                   (deck_id, session['user_id']))
    deck = cursor.fetchone()
    if not deck:
        cursor.close()
        flash('Deck not found or you do not have permission', 'danger')
        return redirect(url_for('dashboard'))

    # Get cards in the deck
    cursor.execute("SELECT * FROM cards WHERE deck_id = %s", (deck_id,))
    cards = cursor.fetchall()

    # Debug print to check if cards are fetched correctly
    print("Cards fetched:", cards)

    # Update the last_studied timestamp for the deck
    now = datetime.now()
    cursor.execute("UPDATE decks SET last_studied = %s WHERE id = %s", 
                   (now, deck_id))
    cnx.commit()
    cursor.close()

    return render_template('study.html', deck=deck, cards=cards)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))
    
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", [session['user_id']])
    user = cursor.fetchone()
    
    if request.method == 'POST':
        email = request.form['email']
        current_password = request.form['current_password']
        
        # Validate current password
        if not check_password_hash(user[3], current_password):  # Assuming password is at index 3
            flash('Current password is incorrect', 'danger')
            cursor.close()
            return render_template('profile.html', user=user)
        
        # Update email
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", 
                   (email, session['user_id']))
        
        # Check if new password was provided
        new_password = request.form['new_password']
        if new_password:
            confirm = request.form['confirm_password']
            
            if new_password != confirm:
                flash('New passwords do not match', 'danger')
                cursor.close()
                return render_template('profile.html', user=user)
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                cursor.close()
                return render_template('profile.html', user=user)
            
            # Update password
            hashed_password = generate_password_hash(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                       (hashed_password, session['user_id']))
        
        cnx.commit()
        cursor.close()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    cursor.close()
    return render_template('profile.html', user=user)

@app.route('/api/cards/<int:deck_id>', methods=['GET'])
def api_get_cards(deck_id):
    if not is_logged_in():
        return jsonify({"error": "Authentication required"}), 401
    
    # Check if deck exists and belongs to user
    cursor = cnx.cursor()
    result = cursor.execute("SELECT * FROM decks WHERE id = %s AND user_id = %s", 
                        [deck_id, session['user_id']])
    
    if result == 0:
        cursor.close()
        return jsonify({"error": "Deck not found or permission denied"}), 403
    
    # Get cards in deck
    cursor.execute("SELECT id, front, back FROM cards WHERE deck_id = %s", [deck_id])
    cards = cursor.fetchall()
    cursor.close()
    
    # Convert to list of dicts for JSON
    cards_list = []
    for card in cards:
        cards_list.append({
            "id": card[0],
            "front": card[1],
            "back": card[2]
        })
    
    return jsonify({"cards": cards_list})

if __name__ == '__main__':
    app.run(debug=True)
