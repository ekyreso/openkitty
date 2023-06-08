from flask import Flask, render_template, request, url_for, send_file, session, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

#configure app
app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

#configure flask session

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#set up the database and database models

db = SQLAlchemy(app)

#database model for the variable of time spent

class PageView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(10))
    page = db.Column(db.String(255))
    time_spent = db.Column(db.Integer)
    start_time = db.Column(db.DateTime)

# Database model for the binary variable: button click
class Button(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(10))
    button = db.Column(db.Boolean)

# Create all the tables for the databases
with app.app_context():
    db.create_all()

# Function to log data: this function saves the time spent on the previous page in the database. Unit of time is seconds.
def log_data():
    try:
        time_spent = (datetime.now() - start_time).total_seconds()

        # First 3 seconds is the threshold to save the time spent in the database. It is to eliminate recording repetitive page requests/reloads.
        if time_spent > 3:
            page_view = PageView(
                visitor_id=session.get('visitor_id'),
                page=previous_path,
                time_spent=time_spent,
                start_time=start_time)
            db.session.add(page_view)
            db.session.commit()
    except:
        pass

# after_request decorator of Flask defines actions to be performed after each request coming from the client-side.
@app.after_request
def track_time(response):
    global start_time
    global previous_path

    # Every time the user requests default route (/), time spent in the previous path is recorded in the database with log_data().
    if request.path == '/':
        log_data()
        # Update start_time and previous_path
        start_time = datetime.now()
        previous_path = 'HomePage'

    # Every time the user requests /learn_more route, time spent in the previous path is recorded in the database with log_data().
    if request.path == '/quiz':
        log_data()
        # Update start_time and previous_path
        start_time = datetime.now()
        previous_path = 'Quiz'

    '''# Every time the user requests  /confirmation route, time spent in the previous path is recorded in the database with log_data().
    if request.path == '/confirmation':
        log_data()
        try:
            # Delete start_time and previous_path variables. Time spent on /confirmation route is not recorded.
            del start_time, previous_path
        except:
            pass'''
    return response


#routes


@app.route ("/")
def index():
    #getting the unique id that will be given by qualtrics to each visitor from the homepage url.
    visitor_id = request.args.get("uid")
    #add it to the session
    if visitor_id:
        session["visitor_id"] = visitor_id
    return render_template("index.html")

@app.route ("/quiz")
def quiz():
    return render_template ("quiz.html")

@app.route("/policy")
def policy():
    return send_file("static/graphs/policy.svg")

@app.route("/trackers")
def trackers():
    return send_file("static/graphs/trackers.svg")

@app.route("/cookies")
def cookies():
    return send_file("static/graphs/cookies.svg")


@app.route("/log_binary")
def button_tracking():
    try:
        button_click = Button(
            visitor_id=session.get('visitor_id'),
            button=True)
        db.session.add(button_click)
        db.session.commit()
    except:
        pass
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(port=3002, debug=True)
