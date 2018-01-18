import peewee as pw
from datetime import datetime


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


class Schedule(BaseModel):
    byUser = pw.ForeignKeyField(User, related_name="set_schedules")
    date = pw.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "schedule"


class HaveSchedule(BaseModel):
    group = pw.ForeignKeyField(Group, "schedules")
    schedule = pw.ForeignKeyField(Schedule, "participant")

    class Meta:
        db_table = "schedule_relation"


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


def inviteUserToGroup(user: User, group: Group) -> Invitation:
    assert not userIsInGroup(user, group)
    assert not userIsInvitedToGroup(user, group)
    q = Invitation(user=user, group=group)
    q.save()
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


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Group, InGroup, MailQueue], safe=True)
