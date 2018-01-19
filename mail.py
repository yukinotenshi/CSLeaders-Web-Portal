from flask import Blueprint, request, render_template, session
import model
import render
from util import loggedIn

mail = Blueprint('mail', 'mail', url_prefix='/mail')


@mail.route("/")
@loggedIn(True)
def view():
    return render.mail()


@mail.route("/send", methods=["POST"])
@loggedIn(True)
def sendMail():
    try:
        print("AAA")
        data = request.form
        user = model.User.get(
            model.User.email == session['user']
        )
        group = model.Group.get(
            model.Group.id == data['group']
        )
        model.broadcastMailToGroup(user, group, data['title'], data['body'])

        return render.mail(success="Mail sent.")

    except Exception as e:
        print(e)
        return render.mail(error="Fail to send email.")
