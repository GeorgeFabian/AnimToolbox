#!/usr/bin/python
import os, re
import sys
import smtplib
from pymel.core import *

from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def saveCurrentFrame(*args):
    filename = sceneName().split("/")[-1]  + ".mov"
    time = getCurrentTime()
    path = playblast(p=50,fr=str(time),f=filename,fo=True)
    return path

def savePlayblast(*args):
    filename = sceneName().split("/")[-1]  + ".mov"
    path = playblast(p=50,f=filename,fo=True)
    return path

def mailUpdate(blast=False,*args):
    sender = promptDialog(
            title='Sender email',
            message='Must be gmail account',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')



    if sender == 'OK':
        sender = promptDialog(q=True, tx=True)
        password = promptDialog(
                    title='Enter password for sender gmail account',
                    message='Password wont be obfuscated or stored.',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

        if password == 'OK':
            password = promptDialog(q=True, tx=True)

            recipient = promptDialog(
                    title='Recipient email',
                    message='Can be any email account',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

            if recipient == 'OK':
                recipient = promptDialog(q=True, tx=True)

                message = promptDialog(
                    title='Add message',
                    message='Message is optional',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

                if message == 'OK':
                    message = promptDialog(q=True, tx=True)
                    update(sender,recipient,message,password)
                    # Thread(target=update, args=(sender,recipient,message,password))
                else:
                    update(sender,recipient,"",password)
                    # Thread(target=update, args=(sender,recipient,"",password))
            else:
                return
        else: 
            return
    else: 
        return
def update(sender,recipient,message,password,*args):

    scene = sceneName().split("/")[-1].split(".")[0]
    if scene == '':
        scene = 'UNTITLED'
    filename = scene  + ".mov"

    path = savePlayblast(filename)


    msg = MIMEMultipart()
    msg['Subject'] = scene + " update"
    msg['To'] = recipient
    msg['From'] = sender 
 
    part = MIMEBase('application','octet-stream')
    pb = open(path,"rb")
    part.set_payload(pb.read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
    msg.attach(part)
 
    part = MIMEText('text', "plain")
    part.set_payload(message)
    msg.attach(part)
 
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
    session.ehlo()
    session.starttls()
    session.ehlo

    session.login(sender, password)
 
    session.sendmail(sender, recipient, msg.as_string())
    session.quit()
