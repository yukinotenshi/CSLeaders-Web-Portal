import model
import sendgrid
from sendgrid.helpers.mail import Mail, Content, Email


class Config(object):
    JOBS = [
            {
                'id': 'sendMail',
                'func': 'scheduler:sendMail',
                'trigger': 'interval',
                'minutes': 1
                }
            ]

    SCHEDULER_API_ENABLED = True


def sendMail():
    print("UYEEEE")

    queue = model.MailQueue \
                 .select(model.MailQueue, model.Broadcast, model.User) \
                 .join(model.Broadcast, model.User) \
                 .order_by(model.MailQueue.sentAt.asc())

    sg = sendgrid.SendGridAPIClient(apikey="SENDGRID_API_KEY")

    for item in queue:
        from_email = Email(item.detail.fromUser.email)
        to_email = Email(item.toUser.email)
        subject = item.detail.body
        content = Content("text/plain", item.detail.title)
        mail = Mail(from_email, subject, to_email, content)
        resp = sg.client.mail.send.post(request_body=mail.get())
        if resp.status_code != 202:
            item.delete_instance()
