
# FlashApp - Flashcard Learning Application

FlashApp is a feature-rich flashcard application built with Flask, MySQL, and Bootstrap that helps users create, organize, and study flashcards efficiently.

## Features

- User account system with registration and login
- Create, edit, and delete flashcard decks
- Organize flashcards by topics/subjects
- Interactive study mode with card flipping
- Progress tracking
- Mobile-responsive design
- Clean and intuitive user interface

## Requirements

- Python 3.7+
- MySQL
- Flask
- Flask-MySQLdb
- PyYAML
- Werkzeug

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/flashapp.git
cd flashapp
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Configure the database:
- Create a MySQL database named `flashapp`
- Import the database schema from `db_setup.sql`
- Edit `db.yaml` with your MySQL credentials

4. Run the application:
```
python app.py
```

5. Open your web browser and navigate to:
```
http://localhost:5000
```

## Usage

1. Register for a new account
2. Create flashcard decks for different subjects
3. Add flashcards to your decks
4. Study your flashcards with the interactive study mode
5. Track your progress over time

## Directory Structure

```
flashapp/
├── app.py                 # Main application file
├── db.yaml                # Database configuration
├── db_setup.sql           # Database schema
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css      # Custom styles
│   ├── img/               # Images and icons
│   └── js/                # JavaScript files
└── templates/             # HTML templates
    ├── index.html         # Landing page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── dashboard.html     # User dashboard
    └── ...                # Other templates
```

## License

MIT

## Acknowledgements

- Bootstrap for the responsive UI components
- Flask for the web framework
- MySQL for the database
