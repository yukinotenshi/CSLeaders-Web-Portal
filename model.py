import peewee as pw
from datetime import datetime, timedelta
from notification import scheduleAdded, scheduleCanceled, groupInvite


db = pw.SqliteDatabase('csl.db')


class BaseModel(pw.Model):
    updatedAt = pw.DateTimeField(default=datetime.now)
    createdAt = pw.DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updatedAt = datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)

    class Meta:
        database = db


class User(BaseModel):
    fullName = pw.CharField()
    nickName = pw.CharField()
    email = pw.CharField()
    password = pw.CharField()
    birth = pw.DateField()

    class Meta:
        db_table = "user"


class Group(BaseModel):
    name = pw.CharField()
    admin = pw.ForeignKeyField(User, related_name="admin_of")

    class Meta:
        db_table = "group"


class InGroup(BaseModel):
    user = pw.ForeignKeyField(User, related_name="groups")
    group = pw.ForeignKeyField(Group, related_name="users")

    class Meta:
        db_table = "ingroup"


class Invitation(BaseModel):
    user = pw.ForeignKeyField(User, related_name="invited_groups")
    group = pw.ForeignKeyField(Group, related_name="invited_users")

    class Meta:
        db_table = "Invitation"


class JoinRequest(BaseModel):
    user = pw.ForeignKeyField(User, related_name="requested_groups")
    group = pw.ForeignKeyField(Group, related_name="requesting_users")

    class Meta:
        db_table = "Invitation"


class Broadcast(BaseModel):
    fromUser = pw.ForeignKeyField(User, related_name="sent_broadcasts")
    toGroup = pw.ForeignKeyField(Group, related_name="received_broadcasts")
    body = pw.TextField()
    title = pw.CharField()

    class Meta:
        db_table = "broadcast"


class MailQueue(BaseModel):
    detail = pw.ForeignKeyField(Broadcast, related_name="sent_emails")
    toUser = pw.ForeignKeyField(User, related_name="received_emails")
    sentAt = pw.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "mailqueue"

class PrivateMailQueue(BaseModel):
    fromUser = pw.ForeignKeyField(User, related_name="sent_privates")
    toUser = pw.ForeignKeyField(User, related_name="received_privates")
    body = pw.TextField()
    title = pw.CharField()
    sent = pw.BooleanField(default=False)
    sentAt = pw.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "private_mail_queue"


class Schedule(BaseModel):
    byUser = pw.ForeignKeyField(User, related_name="set_schedules")
    title = pw.CharField()
    description = pw.TextField()
    date = pw.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "schedule"

class HaveSchedule(BaseModel):
    group = pw.ForeignKeyField(Group, related_name="schedules")
    schedule = pw.ForeignKeyField(Schedule, related_name="groups")

    class Meta:
        db_table = "have_schedule"

class Reminder(BaseModel):
    schedule = pw.ForeignKeyField(Schedule, related_name="reminder")
    date = pw.DateField(default=datetime.today())

    class Meta:
        db_table = "reminder"

def createGroup(name: str, admin: User) -> Group:
    g = Group(name=name, admin=admin)
    g.save()
    InGroup(user=admin, group=g).save()
    return g


def userIsInGroup(user: User, group: Group) -> bool:
    q = InGroup.select() \
               .where((InGroup.user == user) & (InGroup.group == group))
    return q.count() == 1


def userIsInvitedToGroup(user: User, group: Group) -> bool:
    q = Invitation.select() \
               .where((Invitation.user == user) & (Invitation.group == group))
    return q.count() == 1


def inviteUserToGroup(user: User, group: Group, admin : User) -> Invitation:
    assert not userIsInGroup(user, group)
    assert admin == group.admin
    assert not userIsInvitedToGroup(user, group)
    q = Invitation(user=user, group=group)
    q.save()
    pm = PrivateMailQueue(fromUser=admin, toUser=user,
                         title=groupInvite.title % (group.name),
                         body = groupInvite.body % (admin.nickName,
                                               group.name))
    pm.save()

    return q


def addUserToGroup(user: User, group: Group) -> InGroup:
    assert not userIsInGroup(user, group)
    # hapus invitation jika ada
    try:
        q = Invitation \
                .get((Invitation.user == user) & (Invitation.group == group))
        q.delete_instance()
    except Exception as e:
        pass

    # hapus requests jika ada
    try:
        q = JoinRequest \
                .get((JoinRequest.user == user) & (JoinRequest.group == group))
        q.delete_instance()
    except Exception as e:
        pass

    q = InGroup(user=user, group=group)
    q.save()
    return q


def removeUserFromGroup(user: User, group: Group):
    query = InGroup.delete() \
                   .where((InGroup.user == user) & (InGroup.group == group))
    query.execute()


def deleteGroup(group: Group):
    query = InGroup.delete().where(InGroup.group == group)
    query.execute()
    group.delete_instance()


def requestUserToGroup(user: User, group: Group) -> JoinRequest:
    assert not userIsInGroup(user, group)
    assert not userIsInvitedToGroup(user, group)
    q = JoinRequest(user=user, group=group)
    q.save()
    return q


def acceptUserToGroup(r : JoinRequest, admin: User):
    user = r.user
    group = r.group
    assert admin == r.group.admin
    assert not userIsInGroup(user, group)
    assert not userIsInvitedToGroup(user, group)
    q = InGroup(user=user, group=group)
    q.save()


def listUserGroups(user: User):
    return [x.group for x in user.groups]


def listAdminGroups(admin: User):
    return [x for x in admin.admin_of]


def listGroupUsers(group: Group):
    return [x.user for x in group.users]


def listUserInvitationsGroup(user: User):
    return [x.group for x in user.invited_groups]


def broadcastMailToGroup(sender: User, group: Group, title, body):
    b = Broadcast(fromUser=sender, toGroup=group, body=body, title=title)
    b.save()
    for user in listGroupUsers(group):
        m = MailQueue(detail=b, toUser=user)
        m.save()


def addSchedule(user: User, group : Group, title, description, date):
    s = Schedule(byUser=user, title=title, description=description, date=date)
    assert datetime.strptime(date, "%Y-%m-%d") >= datetime.today()
    s.save()
    hs = HaveSchedule(group = group, schedule=s)
    hs.save()
    r = Reminder(schedule=s,
                 date=datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1))
    r.save()
    broadcastMailToGroup(user, group,
                         scheduleAdded.title % (title),
                         scheduleAdded.body % (user.nickName,
                                               title,
                                               description,
                                               date))


def deleteSchedule(schedule: Schedule, user : User):
    assert user == schedule.byUser
    groups = [x.group for x in schedule.groups]
    for group in groups:
        broadcastMailToGroup(schedule.byUser, group,
                             scheduleCanceled.title % (schedule.title),
                             scheduleCanceled.body % (schedule.byUser.nickName,
                                                   schedule.title,
                                                   schedule.description,
                                                   schedule.date))
    schedule.delete_instance()
    query = HaveSchedule.delete().where(
        HaveSchedule.schedule == schedule
    )
    query.execute()
    query = Reminder.delete().where(
        Reminder.schedule == schedule
    )
    query.execute()


def listUserSchedules(user: User):
    groups = listUserGroups(user)
    uniqueSchedules = []
    for group in groups:
        schedules = [x.schedule for x in group.schedules]
        for s in schedules:
            uniqueSchedules.append(s) if s not in uniqueSchedules else None

    def getKey(s):
        return s.date

    return sorted(uniqueSchedules, key=getKey)

if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Group, InGroup, MailQueue], safe=True)
