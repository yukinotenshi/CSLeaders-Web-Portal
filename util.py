from flask import session, render_template
import render

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