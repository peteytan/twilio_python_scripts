"""
This script gets a list of phone numbers for an account and a list of call logs
for a certain date period. It then compares the phone numbers against the call
list to see what numbers have not been used in that period and presents back to
the user, the list of 'unused numbers' and outputs it to a .csv file. It also
provides the option to delete these unused numbers
"""
__author__ = "mjenkinson, ptan"
import datetime
import csv
import os
import gc
from twilio.rest import TwilioRestClient

acct = os.environ['TWILIO_ACCOUNT_SID']
auth = os.environ['TWILIO_AUTH_TOKEN']

# START_AFTER_DATE will get call logs from now going back to the date defined.
# If you have a lot of calls you may want to select a shorter time window.
START_AFTER_DATE = input("Please type in the date to start from in YYYY-MM-DD format: ")

# print('Getting details for Account: ' + ACCT)
client = TwilioRestClient(acct, auth)

# Part One: Get all phone numbers for an account and write to a .csv file.
print('Gathering Phone numbers for this account, the start time is: ' + str(
    datetime.datetime.now().time()))
START_TIME = datetime.datetime.now()

with open("TwilioNumberList.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for number in client.phone_numbers.iter(page_size=1000):
        sid = number.sid
        number = number.phone_number.strip("+")
        writer.writerow([number, sid])
gc.collect()

print('Gathered all the phone numbers, stop time is: ' + str(
    datetime.datetime.now().time()))

# Part Two: Get all call data after the specified date.
print('Gathering call logs for this account, the start time is: ' + str(
    datetime.datetime.now().time()))

with open("TwilioCallLog.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    # If the to / From is blank or is a client we can skip the writing to
    # the file as we only want phone numbers.
    for call in client.calls.iter(page_size=1000,
                                  started_after=START_AFTER_DATE):
        if call.to != None and call.to.startswith("+"):
            writer.writerow([call.to.strip("+")])
        if call.from_ != None and call.from_.startswith("+"):
            writer.writerow([call.from_.strip("+")])
gc.collect()

print('Gathered all the call logs, stop time is: ' + str(
    datetime.datetime.now().time()))

# Part Three: Compare list of numbers owned to numbers in call logs and extract
# owned numbers that have not been used.
print('Scanning for matching phone numbers. Start time:' + str(
    datetime.datetime.now().time()))

call_log_set = set()
number_set = set()

with open("TwilioNumberList.csv") as csvfile:
    number_list = csv.reader(csvfile, delimiter=',')
    for number in number_list:
        number_set.add(number[0])
    csvfile.close()

with open("TwilioCallLog.csv") as callfile:
    call_log = csv.reader(callfile, delimiter=',')
    for number in call_log:
        call_log_set.add(number[0])
    csvfile.close()

unused_list = list(number_set - call_log_set)

print('Done scanning. End time:' + str(datetime.datetime.now().time()))

with open("UnusedNumbers.csv", "w") as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['Phone Number', 'Phone SID'])
    with open("TwilioNumberList.csv", "r") as reference:
        reader = csv.reader(reference)
        numbers = {rows[0]: rows[1] for rows in reader}
        for number in unused_list:
            UNUSED_NUMBERS = {number: numbers[number]}
            writer.writerow([number, numbers[number]])
gc.collect()

print('Script Finished running at: ' + str(datetime.datetime.now().time()))
END_TIME = datetime.datetime.now()
print('Total Time taken was', str(END_TIME - START_TIME))

# Part Four: Delete the Phone Numbers if the user says yes
remove_number = input(
    "Should I delete these unused numbers from the account? Y or N: ")
if (remove_number == 'Y') or (remove_number == 'y'):
    print('Removing unwanted numbers. This may take a while...')
    for sid in unused_list:
        print('Removing ' + sid)
        client.phone_numbers.delete(sid)
    print('Finished removing unused numbers')
else:
    print("Did not remove any numbers")

