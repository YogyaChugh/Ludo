from email.message import EmailMessage
import smtplib
import os

# Send Diagnostics Data on error !
def send_diagnostics_data(e,page):
    print('called')
    if not os.environ.get('email') or not os.environ.get('password'):
        page.update()
        return
    message = ""
    for i in page.session.get('Logs'):
        message += i
        message += "\n--------------------------------------\n\n"
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Diagnostics Data"
    msg['From'] = os.environ.get('email') # Fetched from the env secret's file
    msg['To'] = 'yogya.developer@gmail.com'
    try:
        with smtplib.SMTP('smtp.gmail.com',587) as server:
            server.starttls()
            server.login(os.environ.get('email'),os.environ.get('password'))
            server.sendmail(os.environ.get('email'),'yogya.developer@gmail.com',msg.as_string())
        page.update()
    except Exception as e:
        print('lost')
        print('error: ',e.args[1])
        page.update()
        return