# coding=utf-8

from flask import Flask, request, render_template, session, redirect, url_for
from flask_apscheduler import APScheduler
import scheduler
import hashlib
import model
import render
from group import group
from mail import mail
from util import loggedIn
from schedule import schedule

app = Flask(__name__)
app.secret_key = "SOMETHING SHOULD BE SECRET"
app.register_blueprint(group)
app.register_blueprint(mail)
app.register_blueprint(schedule)

app.config.from_object(scheduler.Config())
schedule = APScheduler()
schedule.init_app(app)
schedule.start()


@app.before_request
def _db_connect():
    if model.db.is_closed():
        model.db.connect()


@app.teardown_request
def _db_close(exc):
    if not model.db.is_closed():
        model.db.close()


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
            user = model.User.get(
                    (model.User.email == data['email']) &
                    (model.User.password == password)
                    )
            session['loggedIn'] = True
            session['user'] = user.email

            return redirect(url_for("dashboard"))
        except Exception as e:
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
    return render.dashboard()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
