"""
This file deletes recordings from a Twilio Account and outputs the
deleted recording info into a .csv file.

It runs as a multi-threaded script, and the threads can be increased to 100,
which is Twilio's default max concurrent API calls you can have.

Currently, it uses the iter() method to grab the entire list of recordings.
It can be changed to a list() method with the relevant filters.
"""
__author__ = 'ptan'

import csv
import os
import threading
from datetime import date
from queue import Queue

import requests
from requests.auth import HTTPBasicAuth
from twilio.rest import TwilioRestClient

# Ensure your environmental variables have these configured
acct = os.environ["TWILIO_ACCOUNT_SID"]
auth = os.environ["TWILIO_AUTH_TOKEN"]

# Flags for toggling functionality
DELETE = True
DOWNLOAD = True

# Initialize Twilio Client
client = TwilioRestClient(acct, auth)

# Create a lock to serialize console output
lock = threading.Lock()


# The work method includes a print statement to indicate progress
def do_work(recording):
    if DOWNLOAD == True:
        # Recordings might be big, so stream and write straight to file
        data = requests.get(recording.uri, auth=HTTPBasicAuth(acct, auth),
                            stream=True)
        with open(recording.sid + '.wav', 'wb') as fd:
            for chunk in data.iter_content(1):
                fd.write(chunk)
        with lock:
            print(threading.current_thread().name, recording.sid, "has downloaded")
    if DELETE == True:
        result = client.recordings.delete(recording.sid)
        with lock:
            print(threading.current_thread().name, "has deleted", recording.sid)


# The worker thread pulls an item from the queue and processes it
def worker():
    while True:
        item = que.get()
        do_work(item)
        que.task_done()


# Create the queue and thread pool. The range value controls number of threads.
que = Queue()
for idx in range(20):
    thread = threading.Thread(target=worker)
    # thread dies when main thread (only non-daemon thread) exits.
    thread.daemon = True
    thread.start()

# Open up a CSV file to dump the results of deleted recordings into
with open('recordings.csv', 'w') as csvfile:
    record_writer = csv.writer(csvfile, delimiter=',')
    # Let's create the header row
    record_writer.writerow(["Recording SID", "Duration", "Date", "Call SID"])
    # The iter() method below will churn out as many recordings as you have.
    # You can use a date filter to reduce this. e.g. before=date(2016, 4, 18)
    for recording in client.recordings.iter(after=date(2015, 6, 1)):
        record_writer.writerow([recording.sid, recording.duration,
                                recording.date_updated, recording.call_sid])
        que.put(recording)
    que.join()  # block until all tasks are done

print("All done!")
