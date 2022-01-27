import smtplib, ssl

password = 'ichwillsaufenbitte69'
mail = 'getraenkefuersjugendheim@gmail.com'


smtp_server = "smtp.gmail.com"
port = 587  # For starttls

class Mail_System:
    def __init__(self):
        pass

    def send_mail(self, receiver_email, message):
        try:
            context = ssl.create_default_context()

            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(mail, password)
                server.sendmail(mail, receiver_email, message)
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.close()