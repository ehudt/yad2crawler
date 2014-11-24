from smtplib          import SMTP, SMTPAuthenticationError


class MailNotifier(object):
    def __init__(self, mail, password):
        self.mail = mail
        self.password = password


    def send_notification(self, recipient, subject, body):
        headers = [
            u"from: " + self.mail,
            u"subject: " + subject,
            u"to: " + recipient,
            u"mime-version: 1.0",
            u"content-type: text/html"
        ]

        headers = u"\r\n".join(headers)
        msg = (headers + u"\r\n\r\n" + body).encode("utf-8")

        try:
            session = SMTP(u"smtp.gmail.com", 587)
            session.ehlo()
            session.starttls()
            session.login(self.mail, self.password)
            session.sendmail(self.mail, recipient, msg)    
            session.quit()
        except SMTPAuthenticationError:
            raise RuntimeError("Wrong mail settings")