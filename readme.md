Twilio Python Master Scripts
============================

What does this do?
------------------
This is a compilation of some commonly used scripts needed in the role of Sales
Engineering either to achieve some task, or to supply a customer with. Some of 
these are scripts to show how a certain function works (Request Validation) or
scripts you can supply a customer with to delete recordings in bulk.

How do I get set up?
--------------------
This uses Python 3.5 and the full requirements can be found in requirements.txt.
THIS IS NOT COMPATIBLE WITH PYTHON 2.X

How do I use this?
------------------
First off, implement "TWILIO_ACCOUNT_SID" and "TWILIO_AUTH_TOKEN" in your local
.bash_profile. The scripts are configured to use these credentials by default. 
You can always replace the variables in the scripts themselves as well.

From that point out, check this readme to see how to use specific scripts and
their intended purposes. The naming convention should be fairly intuitive.

## Operational Scripts
----------------------
### Multi-Threaded Download & Delete Recordings
This file simply takes all the recordings from the account and pushes it to a
CSV file. It puts these recording SIDs into a multi-threaded queue that 
downloads all the recordings into the folder where these scripts sit. The iter() 
method can be replaced with a date-filtered list() method to select a subset of 
recordings. After the recordings are downloaded, they are deleted

Switching DELETE to False will result in just downloading the recordings, and
likewise, switching DOWNLOAD to False will delete the recordings.

### Subaccount Recordings
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

### Purchase Phone Numbers
This script purchases a set of phone numbers that match criteria you specify in 
a .csv file. The script is a single function purchase_phone_numbers that takes 
four arguments: 
phone_numbers_criteria_file_name, 
provision_phone_numbers_flag.

provision_phone_numbers_flag specifies if the script should actually purchase 
the numbers or just simulate a purchase, it accepts either y or n as inputs.
phone_numbers_criteria_file_name is the name of a criteria file formatted in .csv.
A phone number criteria file has a header line that lists all possible 
parameters you can specify as criteria when searching for Twilio phone numbers. 
These criteria are as follows: quantity,country_code,area_code,SmsEnabled,
MmsEnabled,VoiceEnabled,contains,distance,in_lata,in_postal_code,in_rate_center,
in_region,near_lat_long,near_number

For example, the following criteria.csv is searching for 1 number in the USA 
with area code 650, and 5 numbers in the USA in the area code 415 that are SMS 
capable and 2 numbers that are near +16507439658.

```
quantity,country_code,area_code,SmsEnabled,MmsEnabled,VoiceEnabled,contains,distance,in_lata,in_postal_code,in_rate_center,in_region,near_lat_long,near_number
1,US,650,,,,,,,,,,,
5,US,415,,true,,,,,,,,,
2,US,,,,,,,,,,,,+16507439658
```

Once the script has completed it generates a report in a new .csv file that 
takes your criteria file and appends _results to the end.

### Unused Number Finder
This script gets a list of phone numbers for an account and a list of call logs
for a certain date period. It then compares the phone numbers against the call
list to see what numbers have not been used in that period and presents back to
the user, the list of 'unused numbers' and outputs it to a .csv file. It also
provides the option to delete these unused numbers in your shell.



## Example Code
---------------
### Request Validation
This is a simple Flask app to show how you would implement Request Validation
with Twilio. Our documentation gives a rough guide as to how to do it, but this
is a full implementation. There are two main things to note for this:

1) A common mistake is to take GET or GET & POST variables. You only want the 
POST variables to feed into the signature computation. If your RequestURL for
the number has a query string, you need to manually append it before running
the computation.

2) The documentation implies that you only need the main parameters (To, From
, etc) similar to the ones you use when making outbound requests. The function
for validation requires ALL parameters, so just grab the entire request body.
