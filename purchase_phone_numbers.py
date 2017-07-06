"""
A script to purchase phone numbers based on criteria provided by a .csv file
The .csv file should be titled 'phone_numbers_criteria.csv'
By default, this script does not purchase the numbers. Switch the False to True
at the end of this script to actually purchase numbers.
"""
import csv
import os
from twilio.rest import TwilioRestClient

# Replace these with your own credentials
acct = os.environ["TWILIO_ACCOUNT_SID"]
auth = os.environ["TWILIO_AUTH_TOKEN"]


def purchase_phone_numbers(phone_numbers_criteria_file_name,
                           provision_phone_numbers_flag):
    phone_number_criteria = {
        "purchased_quantity": '',
        "quantity": '',
        "country_code": '',
        "area_code": '',
        "SmsEnabled": '',
        "MmsEnabled": '',
        "VoiceEnabled": '',
        "contains": '',
        "distance": '',
        "in_lata": '',
        "in_postal_code": '',
        "in_rate_center": '',
        "in_region": '',
        "near_lat_long": '',
        "near_number": ''
    }

    skip_header = True
    total_pn_purchased = 0
    # Create a Twilio client connection
    client = TwilioRestClient(acct, auth)

    # Output results of purchases to a file
    results_file = phone_numbers_criteria_file_name + '_results.csv'
    fw = open(results_file, mode='w', newline='')
    file_header = ['purchased_quantity', 'quantity', 'country_code',
                   'area_code', 'SmsEnabled', 'MmsEnabled', 'VoiceEnabled',
                   'contains', 'distance', 'in_lata', 'in_postal_code',
                   'in_rate_center', 'in_region', 'near_lat_long',
                   'near_number']
    w = csv.DictWriter(fw, fieldnames=file_header, delimiter=',')
    w.writerow(dict((fn, fn) for fn in file_header))

    # Purchase phone numbers
    # Iterate through each phone purchase criteria and buy the number
    dictReader = csv.DictReader(open(phone_numbers_criteria_file_name, 'r'),
                                fieldnames=['quantity', 'country_code',
                                            'area_code', 'SmsEnabled',
                                            'MmsEnabled', 'VoiceEnabled',
                                            'contains', 'distance', 'in_lata',
                                            'in_postal_code', 'in_rate_center',
                                            'in_region', 'near_lat_long',
                                            'near_number'
                                ], delimiter=',', quotechar='"')
    for row in dictReader:
        if skip_header:
            # print 'File Header: ' + str(row)
            skip_header = False
            continue
        # Process content of csv file
        phone_number_quantity = row['quantity']
        print('Total Phone Numbers Requested: ' + phone_number_quantity)
        current_phone_number_criteria = dict(phone_number_criteria)
        current_phone_number_criteria['quantity'] = row['quantity']
        current_phone_number_criteria['country_code'] = row['country_code']
        current_phone_number_criteria['area_code'] = row['area_code']
        current_phone_number_criteria['SmsEnabled'] = row['SmsEnabled']
        current_phone_number_criteria['MmsEnabled'] = row['MmsEnabled']
        current_phone_number_criteria['VoiceEnabled'] = row['VoiceEnabled']
        current_phone_number_criteria['contains'] = row['contains']
        current_phone_number_criteria['distance'] = row['distance']
        current_phone_number_criteria['in_lata'] = row['in_lata']
        current_phone_number_criteria['in_postal_code'] = row['in_postal_code']
        current_phone_number_criteria['in_rate_center'] = row['in_rate_center']
        current_phone_number_criteria['in_region'] = row['in_region']
        current_phone_number_criteria['near_lat_long'] = row['near_lat_long']
        current_phone_number_criteria['near_number'] = row['near_number']

        # Attempt to get available phone Number
        purchased_numbers_count = 0

        # print "Current Phone Numbers Criteria: "
        # print current_phone_number_criteria
        while (purchased_numbers_count < int(phone_number_quantity)):
            available_phone_numbers = client.phone_numbers.search(
                **current_phone_number_criteria)
            if (available_phone_numbers):
                for p in available_phone_numbers:
                    if (purchased_numbers_count < int(phone_number_quantity)):
                        # This section allows you to test your script without
                        # actually purchasing numbers.
                        if provision_phone_numbers_flag == True:
                            purchased_number = client.phone_numbers.purchase(
                                phone_number = p.phone_number)
                        else:
                            purchased_number = p.phone_number

                        # Make sure we were able to purchase the number
                        if purchased_number:
                            print('Purchased: ' + p.phone_number)
                            # Add incoming phone numbers api call
                            purchased_numbers_count += 1
            else:
                break
        print('Purchased Phone Numbers: ' + str(purchased_numbers_count))
        current_phone_number_criteria[
            'purchased_quantity'] = purchased_numbers_count
        total_pn_purchased = total_pn_purchased + purchased_numbers_count
        # Write the purchase results to output file
        w.writerow(current_phone_number_criteria)
    fw.close()
    print("Total Phone Numbers Purchased::" + str(total_pn_purchased))


# Call the function - Change False to True to actually purchase
purchase_phone_numbers('phone_numbers_criteria.csv', False)