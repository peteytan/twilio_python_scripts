"""
This file looks for all subaccounts and then finds recordings inside all the
subaccounts and the main account, and writes it to a .csv.

It runs as a multi-threaded script, and the threads can be increased to 100,
which is Twilio's default max concurrent API calls you can have.

Currently, it uses the iter() method to grab the entire list of recordings.
It can be changed to a list() method with the relevant filters.

We will have two separate queues, one to pull all the subacounts listed with a
parent account, and the second queues starts taking recordings from these
subaccounts. The resulting csv will be a mess of entries, but this is easily
sorted after

Deleted recordings do not get pulled up in this query
"""
__author__ = 'ptan'

import csv
import httplib2
import threading
from datetime import date
from queue import Queue

from twilio.rest import TwilioRestClient

# Ensure your environmental variables have these configured
acct = os.environ["TWILIO_ACCOUNT_SID"]
auth = os.environ["TWILIO_AUTH_TOKEN"]

# Create a lock to serialize console output
lock = threading.Lock()

# Create master Twilio client session
client = TwilioRestClient(acct, auth)


# The account worker and task handles getting all the account info and creates
# new tasks for the recording worker to take and process
def account_worker():
    while True:
        acct, auth = account_que.get()
        handle_account(acct, auth)
        account_que.task_done()


def handle_account(acct, auth):
    """
    Takes in an account sid and auth token, spins up a new client session and
    starts to pull recordings for that account and places them in the queue
    """
    local_client = TwilioRestClient(acct, auth)
    for recording in local_client.recordings.iter(before=date(2016, 5, 15)):
        recording_que.put((recording, acct))


def recording_worker():
    while True:
        recording, acct = recording_que.get()
        handle_recordings(recording, acct)
        recording_que.task_done()


def handle_recordings(recording, acct):
    """
    For a given recording, pull the wanted metadata and write to file, and then
    delete the file.
    """
    global count
    try:
        client.recordings.delete(recording.sid)
        with lock:
            record_writer.writerow([acct, recording.sid, recording.duration,
                                    recording.date_updated, recording.call_sid,
                                    recording.uri, "Deleted"])
            print(threading.current_thread().name, recording.sid,
                  "written. Count: ", count)
    except:
        with lock:
            record_writer.writerow([acct, recording.sid, recording.duration,
                                    recording.date_updated, recording.call_sid,
                                    recording.uri, "Not Deleted"])
            print(threading.current_thread().name, recording.sid,
                  "written. Count: ", count)
    count += 1


# Create the queue and thread pool. The range value controls number of threads.
account_que = Queue()
recording_que = Queue()
count = 0

# We'll have an I/O rate for recordings 20x as quick as we pull accounts.
for idx1 in range(1):
    thread = threading.Thread(target=account_worker)
    # thread dies when main thread (only non-daemon thread) exits.
    thread.daemon = True
    thread.start()
for idx2 in range(49):
    thread = threading.Thread(target=recording_worker)
    thread.daemon = True
    thread.start()

# Open up a CSV file to dump the results of deleted recordings into
with open('recordings.csv', 'w') as csvfile:
    record_writer = csv.writer(csvfile, delimiter=',')
    # Let's create the header row
    record_writer.writerow(
        ["AccountSID", "Recording SID", "Duration", "Date Updated", "Call SID",
         "Recording URI"])
    # The iter() method below will churn out as many recordings as you have.
    # You can use a date filter to reduce this. e.g. before=date(2016, 4, 18)
    for account in client.accounts.iter():
        # Some subaccounts could be connect apps and thus have a sid but no auth.
        # We want to ensure we don't read the recordings for these accounts
        if account.auth_token == '' or account.status == 'closed' or account.status == 'suspended':
            pass
        else:
            account_que.put((account.sid, account.auth_token))
    account_que.join()  # block until all tasks are done

print("All done!")
