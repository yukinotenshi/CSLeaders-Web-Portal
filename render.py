import model
from flask import render_template, session

def dashboard(**kwargs):
    user = model.User.get(
        model.User.email == session['user']
    )
    mails = [x for x in user.sent_broadcasts] + [x.detail for x in user.received_emails]
    groups = model.list_user_invitations_group(user)
    return render_template("dashboard.html",
                           user=user, mails=mails, groups=groups,
                           page="Dashboard", **kwargs)

def group(**kwargs):
    users = model.User.select()
    user = model.User.get(
        model.User.email == session['user']
    )

    ownedGroups = model.list_admin_groups(user)
    return render_template("group.html",
                           users=users,
                           groups=model.list_user_groups(user),
                           page="Group",
                           ownedGroups=ownedGroups, **kwargs)