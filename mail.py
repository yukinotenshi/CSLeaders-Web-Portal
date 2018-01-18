from flask import Blueprint, request, Response, render_template, url_for, session, redirect
import model
import render

mail = Blueprint('mail', 'mail', url_prefix='/mail')

def loggedIn(bool):
    def decorator(func):
        def wrap(*args, **kwargs):
            if not bool:
                stat = session.get('loggedIn') is None
            else:
                stat = session.get('loggedIn') is not None
            if (stat):
                return func(*args, **kwargs)
            else:
                if bool:
                    return render_template("login.html")
                else:
                    return render.dashboard(success="Logged in.")

        wrap.__name__ = func.__name__
        return wrap
    return decorator

@mail.route("/")
@loggedIn(True)
def view():
    pass