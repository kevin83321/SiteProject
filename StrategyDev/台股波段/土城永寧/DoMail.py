import os
parent = os.path.dirname(os.path.abspath('__file__'))

import warnings
warnings.filterwarnings("ignore")

#==========================
# About Email Server
#==========================
import smtplib
import os
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

def send_mail(send_from, pwd, send_to, subject, text, files=None,
              cc:list=None, server="127.0.0.1", mail_engine='gmail'):
    assert isinstance(send_to, list)
    if cc:
        assert isinstance(cc, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to+cc)
    if cc:
        msg['Cc'] = COMMASPACE.join(cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    # smtp = smtplib.SMTP(server)
    try: 
        if mail_engine == 'gmail':
            smtpObj = smtplib.SMTP('smtp.gmail.com', 587) 
        elif mail_engine == 'outlook':
            smtpObj = smtplib.SMTP('smtp-mail.outlook.com', 587) 
    except Exception as e: 
        print(e) 
        smtpObj = smtplib.SMTP_SSL('smtp-mail.outlook.com', 465) 
    # smtp.sendmail(send_from, send_to, msg.as_string())
    smtpObj.ehlo() 
    smtpObj.starttls() 
    smtpObj.login(send_from, pwd) 
    smtpObj.sendmail(send_from, send_to, msg.as_string()) # Or [email protected] 

    smtpObj.close()

if __name__ == '__main__':

    send_mail('kevin83321@gmail.com', 'yqawneecqdwaluwt', ['akyang0830@outlook.com'], "測試", "測試訊息，不要理我", [], cc=['kevin83321@gmail.com'])