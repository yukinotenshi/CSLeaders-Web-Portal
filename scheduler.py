import model
import sendgrid
from sendgrid.helpers.mail import Mail, Content, Email
from config import __sendgrid_api_key__

class Config(object):
    JOBS = [
            {
                'id': 'sendMail',
                'func': 'scheduler:sendMail',
                'trigger': 'interval',
                'seconds': 30
                }
            ]

    SCHEDULER_API_ENABLED = True


def sendMail():
    if model.db.is_closed():
        model.db.connect()
    queue = model.MailQueue \
                 .select(model.MailQueue, model.Broadcast, model.User) \
                 .join(model.Broadcast) \
                 .join(model.User) \
                 .order_by(model.MailQueue.sentAt.asc())

    sg = sendgrid.SendGridAPIClient(apikey=__sendgrid_api_key__)

    for item in queue:
        from_email = Email(item.detail.fromUser.email)
        to_email = Email(item.toUser.email)
        subject = item.detail.title
        content = Content("text/plain", item.detail.body)
        mail = Mail(from_email, subject, to_email, content)
        resp = sg.client.mail.send.post(request_body=mail.get())
        assert resp.status_code == 202
        item.delete_instance()

    privateQueue = model.PrivateMailQueue.select().where(~model.PrivateMailQueue.sent)

    for item in privateQueue:
        from_email = Email(item.fromUser.email)
        to_email = Email(item.toUser.email)
        subject = item.title
        content = Content("text/plain", item.body)
        mail = Mail(from_email, subject, to_email, content)
        resp = sg.client.mail.send.post(request_body=mail.get())
        assert resp.status_code == 202
        item.sent = True
        item.save()

    if not model.db.is_closed():
        model.db.close()