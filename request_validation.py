"""
This is a example app to show how request validation works with Twilio.

To setup: Have a phone number configured to point to the /inbound_sms endpoint
this server generates with ngrok and append ?foo=1 to the end of that URL.

You will need to create some self-signed SSL certs and keychains as described
here: http://www.akadia.com/services/ssh_test_certificate.html
"""
__author__ = 'ptan'

from flask import Flask, url_for, request
from twilio import twiml
import os
from twilio.util import RequestValidator
import ssl

app = Flask(__name__)

AUTH = os.environ['TWILIO_AUTH_TOKEN']
validator = RequestValidator(AUTH)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.load_cert_chain('myserver.crt', 'myserver.key')


@app.route('/inbound_sms', methods=['POST', 'GET'])
def inbound_sms():
    """
    The endpoint to handle an incoming message.
    """
    # The RequestURL you provided to Twilio. Append any query strings if needed.
    url = url_for('inbound_sms', _external=True)
    url += "?foo=1"
    print("URL:", url)

    # The POST variables attached to the request (eg "From", "To")
    # A common mistake is to get both POST and Query String data.
    post_vars = request.form
    print("POST VARS:", post_vars)

    # Compute and compare X-Twilio-Signature header values
    signature = request.headers.get("X-Twilio-Signature")
    print("Signature:", signature)
    print("Computed Signature:", validator.compute_signature(url, post_vars))

    if validator.validate(url, post_vars, signature):
        print("Confirmed to have come from Twilio.")
        resp = twiml.Response()
        resp.message("Thank you for your text")
        return str(resp)
    else:
        print("NOT VALID.  It might have been spoofed!")
        resp = twiml.Response()
        resp.message("NOT VALID")
        return str(resp)


if __name__ == "__main__":
    app.run(ssl_context=context)
