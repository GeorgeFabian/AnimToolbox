###
# www.colinstanton.com
###

import os, re
import sys
import smtplib
from threading import Thread
import gzip
import zipfile, zlib
import time
import urllib
import urllib2
import urlparse
import oauth2
import glob
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import datetime

from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from pymel.core import *
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
consumer_key="pIwHjLV5A4tBNGvqe5WKmzTMU30UE4OkPguRUrbOX9pYZ4YhpD"
consumer_secret="9XRkW5qx9zz2YU0UO4mDWGWkvwdPgioWAK4QrYtcJsdyMH0VXl"
access_token_url = 'https://www.tumblr.com/oauth/access_token'
 
class howler(OpenMayaMPx.MPxCommand):

    kPluginCmdName = "howler"

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

        self.emailSession = None

        # self.smtpServerField = GMAIL_SMTP_SERVER
        # self.smtpPortField = GMAIL_SMTP_PORT

        if uitypes.Window.exists("sendUpdate"):
            deleteUI('sendUpdate')
        self.win = window('sendUpdate',title="Howler",s=False,w=300)
        windowPref('sendUpdate',w=300)
        
        self.HowlerLayout = frameLayout("Howler",label="")

        # menu(label="Help")
        # menuItem(label="Usage",c=self.displayHelp)
        # menuItem(label="Clear User Info",c=self.clearUserInfo)

        pane = paneLayout("pane",p="Howler")

        tLayout = tabLayout("tabs",p="pane",w=300)

        ############
        ## EMAIL LAYOUT
        emailLayout = frameLayout("Email",label="Email Credentials",p="tabs")

        rowColumnLayout(numberOfColumns=5,columnWidth=[(2,130),(4,15)],columnAttach=[(2,'both',5),(3,'both',5),(4,'both',5),(5,'both',5)],p="Email",w=290)
        text(label="Email")
        self.sender = textField(w=100)
        text(label="Password")
        self.password = textField(fn="smallObliqueLabelFont",w=9,cc=self.signInToEmail)
        self.signInBtn = button(label="Sign In")

        recipientInfoLayout = frameLayout("Recipients",label="Mailing List",p="Email",w=290,cll=True)
        recipientInfoLayout = horizontalLayout(p="Recipients",w=290)
        self.recipient = textField("recipient",ec=self.addRecipient)
        recipientInfoLayout.redistribute()

        addRemoveLayout = horizontalLayout(p="Recipients",w=290)
        self.addRecipientBtn = button(label="Add Recipient")
        self.removeRecipientBtn = button(label="Remove Recipient")
        addRemoveLayout.redistribute()

        recipientListLayout = horizontalLayout(p="Recipients",w=290)
        self.recipientList = textScrollList(allowMultiSelection=True)
        recipientListLayout.redistribute()

        msgLayout = frameLayout("Email Body",p="Email",w=290,cll=True,cl=True)

        self.message = scrollField("message",ww=True,w=180)

        frameLayout("emailSettings",label="Email Settings",p="Email",cll=True,cl=True)
        horizontalLayout(p="emailSettings")
        self.smtpServerField = textField("smtpServer",w=290)
        horizontalLayout(p="emailSettings")
        self.smtpPortField = textField("smtpPort",w=290)
        ## END EMAIL LAYOUT
        ############

        ############
        ## TUMBLR LAYOUT
        frameLayout("Tumblr",label="Tumblr User Credentials",p="tabs")#,cll=True,cl=True)
        rowColumnLayout("TumblrLayout",p="Tumblr")#,cll=True,cl=True)

        rowColumnLayout(numberOfColumns=4,columnWidth=[(2,180),(4,15)],columnAttach=[(2,'both',5),(3,'left',10),(4,'both',5)],p="TumblrLayout",w=290)
        text(label="Email")
        self.tumblrUserEmail = textField(w=180)
        text(label="Password")
        self.tumblrPassword = textField(fn="smallObliqueLabelFont",w=9)
        # tumblrInfoLayout.redistribute()

        rowColumnLayout(numberOfColumns=1,columnWidth=[(1,290)],p="TumblrLayout",w=290)
        self.saveCredsBtn = button(label="Save Tumblr Credentials")
        
        frameLayout("TumblrSettings",p="TumblrLayout",label="")#,cll=True,cl=True)
        rowColumnLayout("token",p="TumblrSettings",numberOfColumns=2,columnWidth=[(1,80),(2,200)],columnAttach=[(1,'right',10),(2,'left',0)])
        text(label="oauthToken",p="token")
        self.oauthTokenField = textField("oauthTokenField",p="token",ed=False,w=200)
        rowColumnLayout("secret",p="TumblrSettings",numberOfColumns=2,columnWidth=[(1,80),(2,200)],columnAttach=[(1,'right',10),(2,'left',0)])
        text(label="oauthToken",p="secret")
        self.oauthTokenSecretField = textField("oauthTokenSecretField",p="secret",ed=False,w=200)
        ## END TUMBLR LAYOUT
        ############

        ############
        ## HELP LAYOUT
        frameLayout("Help",label="Help",p="tabs")
        helpText = """Using Howler:
Right now, Howler has two ways to show the world your work: Email and Tumblr.

================
In the Email tab
================
Enter your email address and password and click Sign In. I'm working to figure out how to obfuscate the password, but Maya isn't making it easy.

If you have two-step authentication for GMail, you'll have to create a application specific password for Howler.

Mailing List
------------
Add the email addresses of your team members, or just whoever you want to share your art with. Facebook allows you to post via email so thats another option!

Email Body
----------
This will be the body of the email.

Email Settings
--------------
Contains information about the smtp server Howler will try to use. The default is smtp.gmail.com for GMail email addresses, but you can change it to whatever you want if you're not using a GMail account.


=================
In the Tumblr tab
=================
Enter the email and password associated with your Tumblr account, and click Update Credentials.

====================
Add Files and Update
====================
You control how you update the world by checking the corresponding checkboxes: Email for Email, Tumblr for Tumblr. Easy peazy.

Add Playblast
-------------
Saves a playblast of the currently selected frames.

Add Current Frame
-----------------
Saves an image of the currently selected frame.

Add External File
-----------------
Select a file from your computer to add.

Delete File
-----------
You can delete files from the list by selecting them in the list and clicking Delete File. You can click and drag to select multiple files at once. Command/Control click to (de)select multiple files.

Once you're satisfied with the contents of the update, click Send/Post Update to share your work with the world!"""
        scrollField(p="Help",ww=True,ed=False,tx=helpText)
        button(label="Reset User Info",c=self.resetUserInfo)
        # END HELP LAYOUT
        #################

        ##############
        # ABOUT LAYOUT

        frameLayout("About",label="About",p="tabs") 

        aboutText = """My name's Colin Stanton, and I'm a recent Computer Science/Digital Art dual major from Northeastern University in Boston!

If you have any questions about Howler or Maya development in general, feel free to shoot me an email at contact@colinstanton.com!
        """
        scrollField(p="About",ww=True,ed=False,tx=aboutText)
        # END ABOUT LAYOUT
        ##################

        ############
        ## HOWLER LAYOUT
        ############
        frameLayout("FileMGMT",p="Howler",label="Add Files and Update")
        rowColumnLayout(p="FileMGMT",numberOfColumns=2)
        # checkBoxLayout = horizontalLayout(p="Howler")
        self.emailCheckBox = checkBox(l="Send Email")
        self.tumblrCheckBox = checkBox(l="Post to Tumblr")
        # checkBoxLayout.redistribute()

        rowColumnLayout(p="FileMGMT",numberOfColumns=3,columnSpacing=[(2,3),(3,3)])
        # addSaveSendLayout = horizontalLayout(p="Howler")
        self.addPlayblastBtn = button(label="Add Playblast")
        self.saveCurrentFrameBtn = button(label="Add Current Frame")
        self.addExternalFileBtn = button(label="Add Extenal File")
        # addSaveSendLayout.redistribute()

        delFilesLayout = paneLayout("delFilesLayout",p="FileMGMT")
        self.deleteFileBtn = button("Delete File",p="delFilesLayout")

        filesLayout = paneLayout("filesLayout",p="FileMGMT")
        self.files = textScrollList("files",p="filesLayout",allowMultiSelection=True)
        updateLayout = horizontalLayout(p="FileMGMT")
        self.doUpdateBtn = button(label="Send/Post Update")
        updateLayout.redistribute()

        self.addPlayblastBtn.setCommand(self.addPlayblast)
        self.saveCurrentFrameBtn.setCommand(self.addScreenshot)
        self.doUpdateBtn.setCommand(self.doUpdate)
        self.addRecipientBtn.setCommand(self.addRecipient)
        self.removeRecipientBtn.setCommand(self.removeRecipient)
        self.deleteFileBtn.setCommand(self.deleteFile)
        self.addExternalFileBtn.setCommand(self.addExternalFile)
        self.saveCredsBtn.setCommand(self.saveCredentials)
        self.signInBtn.setCommand(self.signInToEmail)

    def signInToEmail(self,*args):
        print "---Connecting to %s---" % (str(self.smtpServerField.getText()) + ":" + str(self.smtpPortField.getText()))
        sender = self.sender.getText()
        password = self.password.getText()
        self.emailSession = smtplib.SMTP(self.smtpServerField.getText(), int(self.smtpPortField.getText()),timeout=10)
     
        self.emailSession.ehlo()
        self.emailSession.starttls()
        self.emailSession.ehlo

        print "---Authenticating %s---" % sender

        if password == "":
            passPrompt = promptDialog(
                title='No Password',
                message='Please enter your password',
                button=['Ok', 'Cancel'],
                defaultButton='Yes',
                cancelButton='No',
                dismissString='No')
            password = promptDialog(q=True,text=True)
            if not passPrompt == "Ok" or password == "":
                return
                
        try:
            self.emailSession.login(sender, password)
            confirmDialog( title='Login Successful!',
                            button=['Ok'])
        except:
            confirmDialog( title='Login Failed', 
                         message='Username and Password not accepted.', 
                         button=['Ok'])

    def deleteFile(self,*args):
        selection = self.files.getSelectItem()

        for f in selection:
            files = self.files.getAllItems()
            files.remove(f)
            self.files.removeAll()
            self.files.append(files)

    def getTimeStamp(self,*args):
        return str(datetime.datetime.now()).split(" ")[0]

    def addRecipient(self, *args):
        recipient = self.recipient.getText()
        if not recipient == "":
            self.recipientList.append(recipient)

    def removeRecipient(self, *args):

        selection = self.recipientList.getSelectItem()
        if not len(selection) >= 1:
            warning("No recipient selected")
            return

        for recip in selection:
            recipients = self.recipientList.getAllItems()
            recipients.remove(recip)
            self.recipientList.removeAll()
            self.recipientList.append(recipients)

    def setSmtpInfo(server,port,*args):
        self.smtpServerField.setText(server)
        self.smtpPortField.setText(port)

    def saveUserInfo(self,*args):
        sb = ""
        sb += "sender:%s||" % self.sender.getText()
        sb += "recipients:%s||" % ",".join(self.recipientList.getAllItems())
        sb += "tumblrUserEmail:%s||" % self.tumblrUserEmail.getText()
        sb += "smtp_server:%s||" % self.smtpServerField.getText()
        sb += "smtp_port:%s||" % self.smtpPortField.getText()
        sb += "emailCB:%s||" % checkBox(self.emailCheckBox,q=True,v=True)
        sb += "tumblrCB:%s||" % checkBox(self.tumblrCheckBox,q=True,v=True)
        sb += "oauthToken:%s||" % self.oauthTokenField.getText()
        sb += "oauthTokenSecret:%s" % self.oauthTokenSecretField.getText()
        f = open(workspace.path+"/data/userInfo.txt","wb+")
        f.write(sb)
        f.close()

    def resetUserInfo(self, *args):
        dataDir = os.path.join(workspace.path,"data")
        userInfo = os.path.join(dataDir,"userInfo.txt")
        userInfo = open(userInfo,"wb+")
        sb = ""
        sb += "smtp_server:smtp.gmail.com||"
        sb += "smtp_port:587"
        userInfo.write(sb)

        self.sender.setText("")
        self.password.setText("")
        self.recipientList.removeAll()
        # self.recipientList,e=True,label="%d" % len(self.recipientList.getAllItems())
        self.recipientList.label("TEST")
        self.tumblrUserEmail.setText("")
        self.oauthTokenField.setText("")
        self.oauthTokenSecretField.setText("")
        self.smtpServerField.setText("smtp.gmail.com")
        self.smtpPortField.setText("587")
        checkBox(self.emailCheckBox,q=True,v=False)
        checkBox(self.tumblrCheckBox,q=True,v=False)
        self.files.removeAll()

    def clearUserInfo(self,*args):
        dataDir = os.path.join(workspace.path,"data")
        userInfo = os.path.join(dataDir,"userInfo.txt")
        if os.path.isfile(userInfo):
            os.remove(userInfo)

    def loadUserInfo(self,*args):
        dataDir = os.path.join(workspace.path,"data")
        userInfo = os.path.join(dataDir,"userInfo.txt")
        if os.path.isfile(userInfo):
            f = open(userInfo,"rb")
            content = f.read()
            content = self.getValueDict(content)
            keys = content.keys()
            if "sender" in keys:
                senderInfo = content["sender"]
                self.sender.setText(senderInfo)
            if "recipients" in keys:
                recipients = content["recipients"].split(",")
                for recipient in recipients:
                    self.recipientList.append(recipient)
            if "tumblrUserEmail" in keys:
                tumblrUserEmail = content["tumblrUserEmail"]
                self.tumblrUserEmail.setText(tumblrUserEmail)
            if "smtp_server" in keys:
                smtp_server = content["smtp_server"]
                if smtp_server == "":
                    self.smtpServerField.setText("smtp.gmail.com")
                else:
                    self.smtpServerField.setText(smtp_server)
                self.smtpServerField.setText(smtp_server)
            if "smtp_port" in keys:
                smtp_port = content["smtp_port"]
                if smtp_port == "":
                    self.smtpPortField.setText(587)
                else:
                    self.smtpPortField.setText(smtp_port)
            if "emailCB" in keys:
                emailCB = content["emailCB"] == 'True'
                checkBox(self.emailCheckBox,e=True,v=emailCB)
            if "tumblrCB" in keys:
                tumblrCB = content["tumblrCB"] == 'True'
                checkBox(self.tumblrCheckBox,e=True,v=tumblrCB)
            if "oauthToken" in keys:
                oauthToken = content["oauthToken"]
                self.oauthTokenField.setText(oauthToken)
            if "oauthTokenSecret" in keys:
                oauthTokenSecret = content["oauthTokenSecret"]
                self.oauthTokenSecretField.setText(oauthTokenSecret)
            f.close()
        else:
            self.smtpServerField.setText("smtp.gmail.com")
            self.smtpPortField.setText("587")
            print "No user info is currently saved."

    def getValueDict(self,content,*args):
        valueDict = {}
        content = content.split("||")
        for val in content:
            key = val.split(":")[0]
            value = val.split(":")[1]
            valueDict[key] = value
        return valueDict

    def getCredentials(self,tumblr,newCreds=False,*args):
        token = self.oauthTokenField.getText()
        secret = self.oauthTokenSecretField.getText()
        user = self.tumblrUserEmail.getText()
        password = self.tumblrPassword.getText()
        if not token == "" and not secret == "" and not newCreds:
            response = tumblr.authenticate(oauthToken=token,oauthTokenSecret=secret)
        else:
            response = tumblr.authenticate(user=user,password=password)

        if response['status'] == '200':
            self.oauthTokenField.setText(tumblr.oauthToken)
            self.oauthTokenSecretField.setText(tumblr.oauthTokenSecret)
        else:
            confirmDialog( title='Tumblr Authentication Failed', 
                         messageAlign='center',
                         message='Username and Password not accepted.', 
                         button=['Ok'])


        return tumblr
         
    def saveCredentials(self,*args):
        self.getCredentials(tumblrPost(),newCreds=True)
        self.saveUserInfo()

    def doUpdate(self,*args):
        filePaths = self.files.getAllItems()
        email = checkBox(self.emailCheckBox,q=True,v=True)
        tumblr = checkBox(self.tumblrCheckBox,q=True,v=True)
        tumblrAuth = self.getCredentials(tumblrPost())
        self.saveUserInfo()

        if len(filePaths) > 0:
            
            if email:
                self.sendEmail(self.sender.getText(),
                       self.recipientList.getAllItems(),
                       self.message.getText(),
                       self.password.getText(),
                       filePaths)
            if tumblr:
                self.postToTumblr(tumblrAuth,filePaths)
        else:
            sendNoFiles = confirmDialog( title='Confirm', 
                                         message='"No files added, send update anyways?"', 
                                         button=['Send','Cancel'])

            if sendNoFiles == "Send" and email:
                self.sendEmail(self.sender.getText(),
                           self.recipientList.getAllItems(),
                           self.message.getText(),
                           self.password.getText(),
                           filePaths)
                # Text post to tumblr?
            else:
                return

    def savePlayblast(self,*args):
        path = playblast(p=100,filename=sceneName()+str(len(self.files.getAllItems()))+".mov",fo=True)
        return path

    def addExternalFile(self,*args):
        path = fileDialog()
        if path:
            self.files.append(path)

    def saveCurrentFrame(self,*args):
        # os.system("screencapture -w %s/%s" % (workspace.path+"/images",filename))
        frame = currentTime()
        filename = os.path.basename(sceneName()).split(".")[0]
        filename += str(len(self.files.getAllItems()))

        path = playblast(p=100,fr=frame,format="image",v=False).replace("#","0")
        badImgName = open(path,"rb").read()
        os.remove(path)

        path = os.path.join(workspace.path,"images")
        path = os.path.join(path,"%s.png" % filename)
        frameImg = open(path ,"w+").write(badImgName)
        return path

    def addPlayblast(self,*args):

        print "---Playblasting scene---"
        path = self.savePlayblast()

        self.files.append(path)

    def addScreenshot(self,*args):

        #Set image format to PNG
        eval("setAttr (\"defaultRenderGlobals.imageFormat\",32)")

        print "---Saving Current Frame---"
        path = self.saveCurrentFrame()

        self.files.append(path)

    def postToTumblr(self,session,filePaths,*args):
        photos = []
        videos = []
        if len(filePaths) >= 1:
            files = self.addCaptions(filePaths)
            for f in files:
                filename = f[0].split(".")[-2]
                extension = f[0].split(".")[-1]
                if extension == "mov":
                    videos.append(f)
                else:
                    photos.append(f)

        session.postContent(photos,"photo")
        session.postContent(videos,"video")


    def addCaptions(self,filePaths,*args):
        files = []
        for i in range(len(filePaths)):
            img = filePaths[i]
            captionWindow = window('captionWindow') 
            pLayout = rowColumnLayout() 
            image( image=img) 

            showWindow( captionWindow ) 

            captionPrompt = promptDialog(
                            title='Add a caption?',
                            message='Caption:',
                            button=['Yes', 'Caption the rest', 'No', 'No more captions'])

            caption = promptDialog(q=True,text=True)

            if captionPrompt == "Yes":
                files.append((img,caption))
                deleteUI('captionWindow')
            elif captionPrompt == "Caption the rest":
                for img in filePaths[i:]:
                    files.append((img,caption))
                deleteUI('captionWindow')
                break
            elif captionPrompt == "No":
                deleteUI('captionWindow')
                continue
            elif captionPrompt == "No more captions":
                for img in filePaths[i:]:
                    files.append((img,""))
                deleteUI('captionWindow')
                break
        return files

    def sendEmail(self,sender,recipients,message,password,filePaths):
        start = time.time()
        if not self.emailSession:
            passPrompt = confirmDialog(
                    title='No active email session',
                    message='Please sign in at the top of the Email tab',
                    button=['Ok'])
            return
        if len(recipients) > 1:
            for r in recipients:
                if not "@" in r:
                    recipients.remove(r)
            recipient = ">,<".join(recipients)
            recipient = "<%s>" % recipient
        elif len(recipients) == 1:
            recipient = "<%s>" % recipients[0]
        else: 
            warning("No recipients specified")
            return

        # saveFile = promptDialog(
        #     title='Save file',
        #     message='Save file before updating?',
        #     text=sceneName().splitpath()[1],
        #     button=['Save','Don\'t Save'],
        #     defaultButton='Yes',
        #     cancelButton='No',
        #     dismissString='No')
        
        # if saveFile == 'Save':
        #     saveName = promptDialog(q=True,text=True)
        #     saveFile(str(saveName))

        

        scene = "%s %s" % (sceneName().splitpath()[1],self.getTimeStamp())

        msg = MIMEMultipart()
        msg['Subject'] = "Updates from %s " % scene
        msg['To'] = recipient
        msg['From'] = sender 
     
        if len(filePaths) >= 1:
            print "---Encoding Attachments---"

            emailZipFileName = "email_%d.zip" % int(time.time())
            emailZipPath = "%s/data/%s" % (workspace.path,emailZipFileName)

            emailZip = zipfile.ZipFile(emailZipPath, mode='w')

            for i in range(len(filePaths)):
                path = filePaths[i]
                print "FILE   " + path
                file = open(path,"rb").read()
                emailZip.write(path,arcname=os.path.basename(path),compress_type=zipfile.ZIP_DEFLATED)

            print emailZipPath

            emailZip.close()

            scene = sceneName().splitpath()[1]

            part = MIMEBase('application','octet-stream')
            out = open(emailZipPath,"rb").read()
            part.set_payload(out)
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % (emailZipFileName))
            msg.attach(part)

     
        part = MIMEText('text', "plain")
        part.set_payload(message)
        msg.attach(part)
        print "---Sending Email with %d file(s)---" % len(filePaths)
        self.emailSession.sendmail(sender, recipient, msg.as_string())
        # self.emailSession.quit()
        self.files.removeAll()

    def doIt(self,args):
        self.loadUserInfo()
        # allowedAreas = ['right', 'left']
        # dockControl( area='left', content=self.HowlerLayout, allowedArea=allowedAreas )
        self.win.show()
        # allowedAreas = ['right', 'left']
        # dockControl( area='right', content=self.win, label='Label',  allowedArea=allowedAreas )


class tumblrPost():

    def __init__(self):
        self.userData = None
        self.url = "http://api.tumblr.com"
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.oauthToken = None
        self.oauthTokenSecret = None
        self.token = None
        self.userData = None
        register_openers()


    def authenticate(self,user=None,password=None,oauthToken=None,oauthTokenSecret=None):
        
        if user and password:
            user = user
            password = password
            client = oauth2.Client(self.consumer)
            client.add_credentials(user,password)
            client.authorizations
             
            params = {}
            params["x_auth_username"] = user
            params["x_auth_password"] = password
            params["x_auth_mode"] = 'client_auth'
         
            client.set_signature_method = oauth2.SignatureMethod_HMAC_SHA1()
            resp, token = client.request(access_token_url, method="POST",body=urllib.urlencode(params))
            if not resp['status'] == '200':
                return resp
            access_token = dict(urlparse.parse_qsl(token))
            self.oauthToken = access_token['oauth_token']
            self.oauthTokenSecret = access_token['oauth_token_secret']
            self.token = oauth2.Token(access_token['oauth_token'], access_token['oauth_token_secret'])
        elif oauthToken and oauthTokenSecret:
            self.oauthToken = oauthToken
            self.oauthTokenSecret = oauthTokenSecret
            self.token = oauth2.Token(self.oauthToken, self.oauthTokenSecret)

         
        client = oauth2.Client(self.consumer, self.token)
        resp, user_data = client.request('http://api.tumblr.com/v2/user/info', method="POST")
        self.userData = json.loads(user_data)
        return resp


    def getUrl(self):
        return self.userData["response"]["user"]["blogs"][0]["url"][7:-1]

    def postContent(self,files,contentType,tags=""):
        for f in files:
            content = f[0]
            caption = f[1]
            print "---Posting %s file---" % contentType
            date  = time.gmtime(os.path.getmtime(content))
            post = {
                'type' : contentType,
                'date' : time.strftime ("%Y-%m-%d %H:%M:%S", date),
                'data' : content,
                'tags' : tags,
                'caption' : caption
            }
         
            try:
                response = self.createPost(self.getUrl(),post)
            except APIError:
                print "Error"
                break
        


    def parse_response(self, result):
        content = json.loads(result)
        if 400 <= int(content["meta"]["status"]) <= 600:
            raise APIError(content["meta"]["msg"], result)
        return content["response"]
 
    def createPost(self, id, post):
        url = self.url + "/v2/blog/%s/post" %id
 
        postFile = post['data']
        del(post['data'])
        req = oauth2.Request.from_consumer_and_token(self.consumer,
                                                 token=self.token,
                                                 http_method="POST",
                                                 http_url=url,
                                                 parameters=post)
        req.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), self.consumer, self.token)
        compiled_postdata = req.to_postdata()
        all_upload_params = urlparse.parse_qs(compiled_postdata, keep_blank_values=True)
 
        for key, val in all_upload_params.iteritems():
            all_upload_params[key] = val[0]
 
        all_upload_params['data'] = open(postFile, 'rb')
        datagen, headers = multipart_encode(all_upload_params)
        request = urllib2.Request(url, datagen, headers)
 
        try:
            respdata = urllib2.urlopen(request).read()
        except urllib2.HTTPError, ex:
            return 'Received error code: ', ex.code
 
        return self.parse_response(respdata)



class APIError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg) 
    

def cmdCreator():
    return OpenMayaMPx.asMPxPtr( howler() )

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( howler.kPluginCmdName, cmdCreator)
    except:
        sys.stderr.write( "Failed to register command: %s" % howler.kPluginCmdName )
        raise
 
# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( howler.kPluginCmdName )
    except:
        sys.stderr.write( 'Failed to unregister command: ' + howler.kPluginCmdName )
        raise


