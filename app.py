import os

from flask import Flask, session, request, jsonify, render_template, flash, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from config import DevelopmentConfig
from forms import LoginForm
from flask_login import LoginManager, current_user, login_user, logout_user




app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))
db = SQLAlchemy(app)

# set up login LoginManager
login = LoginManager(app)

from models import Book, User, Review


@app.route("/", methods=['GET', 'POST'])
@app.route("/index")
def index():
    user = {'username': 'Nyasha'}
    reviews = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, reviews=reviews)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
 
@app.route("/add")
def add_book():
    name=request.args.get('name')
    author=request.args.get('author')
    published=request.args.get('published')
    try:
        book=Book(
            name=name,
            author=author,
            published=published
        )
        db.session.add(book)
        db.session.commit()
        return f"Book added. book id={book.id}"
    except Exception as e:
	    return(str(e))

@app.route("/getall")
def get_all():
    try:
        books=Book.query.all()
        return  jsonify([e.serialize() for e in books])
    except Exception as e:
	    return(str(e))

@app.route("/get/<id_>")
def get_by_id(id_):
    try:
        book=Book.query.filter_by(id=id_).first()
        return jsonify(book.serialize())
    except Exception as e:
	    return(str(e))


@app.route("/add/form",methods=['GET', 'POST'])
def add_book_form():
    if request.method == 'POST':
        name=request.form.get('name')
        author=request.form.get('author')
        published=request.form.get('published')
        try:
            book=Book(
                name=name,
                author=author,
                published=published
            )
            db.session.add(book)
            db.session.commit()
            return f"Book added. book id={book.id}"
        except Exception as e:
            return(str(e))
    return render_template("getdata.html")





@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Review': Review}


if __name__ == '__main__':
    app.run()



