import model
from flask import render_template, session

def sortMail(m):
    return m.createdAt

def dashboard(**kwargs):
    user = model.User.get(
        model.User.email == session['user']
    )
    mails = sorted(list(set([x for x in user.sent_broadcasts] + \
                            [x.detail for x in user.received_emails])), key=sortMail, reverse=True)
    groups = model.listUserInvitationsGroup(user)
    return render_template("dashboard.html",
                           user=user, mails=mails, groups=groups,
                           page="Dashboard", **kwargs)

def group(**kwargs):
    users = model.User.select()
    user = model.User.get(
        model.User.email == session['user']
    )

    ownedGroups = model.listAdminGroups(user)
    return render_template("group.html",
                           users=users,
                           groups=model.listUserGroups(user),
                           page="Group",
                           ownedGroups=ownedGroups, **kwargs,
                           admin=user)

def mail(**kwargs):
    user = model.User.get(
        model.User.email == session['user']
    )
    groups = model.Group.select()
    mails = sorted(list(set([x for x in user.sent_broadcasts] + \
                            [x.detail for x in user.received_emails])), key=sortMail, reverse=True)

    return render_template("mail.html",
                           page="Mail",
                           groups=groups,
                           mails=mails,
                           user=user, **kwargs)


def schedule(**kwargs):
    user = model.User.get(
        model.User.email == session['user']
    )
    schedules = model.listUserSchedules(user)
    groups = model.listUserGroups(user)

    return render_template("schedule.html",
                           page="Schedule",
                           user=user,
                           schedules=schedules,
                           groups=groups, **kwargs)