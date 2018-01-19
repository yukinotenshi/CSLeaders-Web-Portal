from flask import Blueprint, request, Response, render_template, url_for, session, redirect
import model
import render
from util import loggedIn

schedule = Blueprint('schedule', 'schedule', url_prefix='/schedule')

@schedule.before_request
def _db_connect():
    if model.db.is_closed():
        model.db.connect()


@schedule.teardown_request
def _db_close(exc):
    if not model.db.is_closed():
        model.db.close()


@schedule.route("/")
@loggedIn(True)
def view():
    return render.schedule()

@schedule.route("/set", methods=["POST"])
@loggedIn(True)
def setSchedule():
    try:
        data = request.form
        user = model.User.get(
            model.User.email == session['user']
        )
        group = model.Group.get(
            model.Group.id == data['group']
        )

        model.addSchedule(
            user, group,
            data['title'],
            data['description'],
            data['date']
        )

        return render.schedule(success="Schedule has been added.")
    except Exception as e:
        print(e)
        return render.schedule(error="Fail setting schedule.")

@schedule.route("/delete/<sid>")
@loggedIn(True)
def delete(sid):
    try:
        schedule = model.Schedule.get(
            model.Schedule.id == sid
        )
        user = model.User.get(
            model.User.email == session['user']
        )
        model.deleteSchedule(schedule, user)

        return render.schedule(success="Schedule has been deleted.")
    except Exception as e:
        print(e)
        return render.schedule(error="Fail deleting schedule.")