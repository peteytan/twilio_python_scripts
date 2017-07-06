"""
This file gets all phone numbers from a Twilio Account and outputs the
phone number and its info into a .csv file.

Currently, it uses the iter() method to grab the entire list of recordings.
It can be changed to a list() method with the relevant filters.
"""

from twilio.rest import TwilioRestClient
import csv
import os

acct = os.environ["TWILIO_ACCOUNT_SID"]
auth = os.environ["TWILIO_AUTH_TOKEN"]

# Initialize Twilio Client
client = TwilioRestClient(acct, auth)

# Open up a CSV file to dump the results of deleted recordings into
with open('phone_numbers_dump.csv', 'w') as csvfile:
    phonenum_writer = csv.writer(csvfile, delimiter=',')
    # The iter() method below will churn out as many recordings as you have.
    # If you have a large amount, use list(DateCreated>=YYYY-MM-DD,
    # DateCreated <=YYYY-MM-DD) to filter by specific time windows.
    phonenum_writer.writerow(["SID", "Created Date", "Updated Date",
                              "Friendly Name", "Phone Number",
                              "Voice App SID", "Voice URL", "Voice Method",
                              "Voice Fallback URL", "Voice Fallback Method",
                              "Status Callback URL", "Status Callback Method",
                              "SMS App SID", "SMS URL", "SMS Method",
                              "SMS Fallback URL", "SMS Fallback Method", ])
    # This goes through the whole list and writes to the CSV file before
    # placing the job in the queue for recording deletes.
    for number in client.phone_numbers.iter():
        phonenum_writer.writerow([number.sid, number.date_created,
                                  number.date_updated, number.friendly_name,
                                  number.phone_number,
                                  number.voice_application_sid,
                                  number.voice_url, number.voice_method,
                                  number.voice_fallback_url,
                                  number.voice_fallback_method,
                                  number.status_callback,
                                  number.status_callback_method,
                                  number.sms_application_sid,
                                  number.sms_url, number.sms_method,
                                  number.sms_fallback_url,
                                  number.sms_fallback_method])







