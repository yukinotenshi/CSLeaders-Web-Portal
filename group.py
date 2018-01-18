from flask import Blueprint, request, Response, render_template, url_for, session, redirect
import model
import render

group = Blueprint('group', 'group', url_prefix='/group')

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


@group.before_request
def _db_connect():
    if model.db.is_closed():
        model.db.connect()


@group.teardown_request
def _db_close(exc):
    if not model.db.is_closed():
        model.db.close()


@group.route("/")
@loggedIn(True)
def view():
    return render.group()


@group.route("/accept/<gid>")
@loggedIn(True)
def accept(gid):
    try:
        user = model.User.get(
            model.User.email == session['user']
        )
        group = model.Group.get(
            model.Group.id == gid
        )
        model.addUserToGroup(user, group)

        return render.dashboard(success="Successfully joined group")
    except:
        return render.dashboard(error="Fail joining group")


@group.route("/decline/<gid>")
@loggedIn(True)
def decline(gid):
    try:
        user = model.User.get(
            model.User.email == session['user']
        )
        group = model.Group.get(
            model.Group.id == gid
        )
        invitation = model.Invitation.get(
            (model.Invitation.user == user) &
            (model.Invitation.group == group)
        )

        invitation.delete_instance()

        return render.dashboard(success="You have declined the invitation.")
    except:
        return render.dashboard(error="An error occured")


@group.route("/create", methods=["POST"])
@loggedIn(True)
def create():
    groupName = request.form['group']
    user = model.User.get(
        model.User.email == session['user']
    )
    model.createGroup(groupName, user)

    return render.group(success="Group has been created.")


@group.route("/delete", methods=["POST"])
@loggedIn(True)
def delete():
    try:
        group = model.Group.get(model.Group.id == request.form['id'])
        model.deleteGroup(group)
        return render.group(success="Group has been deleted")
    except:
        return render.group(error="Fail deleting group")


@group.route("/invite", methods=["POST"])
@loggedIn(True)
def invite():
    try:
        data = request.form
        user = model.User.get(
            model.User.id == data['user']
        )
        group = model.Group.get(
            model.Group.id == data['group']
        )

        model.inviteUserToGroup(user, group)

        return render.group(success="You have invited %s" % user.nickName)

    except:
        return render.group(error="Error inviting %s" % user.nickName)
