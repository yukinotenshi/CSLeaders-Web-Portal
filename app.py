# coding=utf-8

from flask import Flask, request, abort, send_file, render_template, redirect, session
import hashlib
from model import *

app = Flask(__name__)

app.secret_key = "SOMETHING SHOULD BE SECRET"

def loggedIn(bool):
    def decorator(func):
        def wrap(*args, **kwargs):
            if not bool:
                stat = session.get('loggedIn') == None
            else:
                stat = session.get('loggedIn') != None
                print(stat)
            if (stat):
                return func(*args, **kwargs)
            else:
                if bool:
                    return render_template("login.html")
                else:
                    return render_template("dashboard.html")

        wrap.__name__ = func.__name__
        return wrap
    return decorator

@app.before_request
def _db_connect():
    if db.is_closed():
        db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route("/", methods=["GET", "POST"])
@loggedIn(False)
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        try:
            data = request.form
            m = hashlib.md5()
            m.update(request.form['password'].encode('utf-8'))
            password = m.hexdigest()
            user = User.get((User.email == data['email']) & (User.password == password))
            session['loggedIn'] = True
            session['user'] = user.fullName

            return render_template("dashboard.html", success = "Successfully logged in.")
        except Exception as e:
            print(e)
            return render_template("login.html", msg="Wrong email/password.")

@app.route('/logout')
@loggedIn(True)
def logout():
    session.pop('loggedIn', None)
    session.pop('user', None)
    return render_template("login.html")

@app.route("/dashboard")
@loggedIn(True)
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)