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


class Broadcast(BaseModel):
    fromUser = pw.ForeignKeyField(User, related_name="sent_broadcasts")
    toGroup = pw.ForeignKeyField(Group, related_name="received_broadcasts")
    body = pw.TextField()
    title = pw.CharField()
    isQueued = pw.BooleanField()

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
    forGroup = pw.ForeignKeyField(Group, related_name="received_schedules")
    date = pw.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "schedule"

def create_group(name: str, admin: User) -> Group:
    g = Group(name=name, admin=admin)
    g.save()
    InGroup(user=admin, group=g).save()
    return g


def user_is_in_group(user: User, group: Group) -> bool:
    q = InGroup.select() \
               .where((InGroup.user == user) & (InGroup.group == group))
    return q.count() == 1


def user_is_invited_to_group(user: User, group: Group) -> bool:
    q = Invitation.select() \
               .where((Invitation.user == user) & (Invitation.group == group))
    return q.count() == 1


def invite_user_to_group(user: User, group: Group) -> Invitation:
    assert not user_is_in_group(user, group)
    assert not user_is_invited_to_group(user, group)
    q = Invitation(user=user, group=group)
    q.save()
    return q


def add_user_to_group(user: User, group: Group) -> InGroup:
    assert not user_is_in_group(user, group)
    # hapus invitation jika ada
    try:
        q = Invitation \
                .get((Invitation.user == user) & (Invitation.group == group))
        q.delete()
    except Exception as e:
        print(e)
        pass
    q = InGroup(user=user, group=group)
    q.save()
    return q


def delete_group(group: Group):
    InGroup.delete().where(InGroup.group == group)
    group.delete_instance()


def list_user_groups(user: User):
    return [x.group for x in user.groups]


def list_group_users(group: Group):
    return [x.user for x in group.users]

def list_user_invitations_group(user: User):
    return [x.group for x in user.invited_groups]


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Group, InGroup, MailQueue], safe=True)