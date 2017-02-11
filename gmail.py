import httplib2

from oauth2client import client
from apiclient import discovery
from apiclient.http import BatchHttpRequest
from oauth2client import client

from email.utils import parseaddr


def get_credentials(flask_sess_cred):
    """Returns a credentials object of Google API from the json config"""

    credentials = client.OAuth2Credentials.from_json(flask_sess_cred)

    return credentials


def get_auth_flow(redirect_uri):
    """Returns a flow object from Google API for gmail"""

    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/gmail.readonly',
        redirect_uri=redirect_uri)
    
    return flow
    

def get_messages(credentials, page_token=None):
    """Get a list of personal messages from the INBOX
    either first page or a specific page"""

    datalist = []

    def insert_message_result(request_id, response, exception):
        datalist.append(response)            

    credentials = client.OAuth2Credentials.from_json(credentials)

    http_auth = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http_auth)

    mail_list = []

    batch = service.new_batch_http_request(callback=insert_message_result)

    response = service.users().messages().list(userId='me', labelIds=['INBOX', 'CATEGORY_PERSONAL'], pageToken=page_token, maxResults=1000).execute()

    for mail in response['messages']:
        batch.add(service.users().messages().get(userId='me', id=mail['id'], format='metadata'))

    batch.execute()

    nextPageToken = None

    if 'nextPageToken' in response:
        nextPageToken = response['nextPageToken']

    response = {
            'datalist': datalist,
            'nextPageToken': nextPageToken,
            'resultSizeEstimate': response['resultSizeEstimate']
    }

    return response


def get_emails_from_messages(messages):
    """Returns the list of contacts and their email addresses from a
    list of gmail messages"""

    contacts = {}

    for message in messages:
        if message:
            for header in message['payload']['headers']:
                if header['name'] == 'From':
                    header_val = parseaddr(header['value'])

                    if header_val in contacts:
                        contacts[header_val] += 1
                    else:
                        contacts[header_val] = 1

    return contacts


def process_user_messages_async(credentials):
    response = get_messages(credentials)
    emails = get_emails_from_messages(response['datalist'])

    while response['nextPageToken']:
        response = get_messages(credentials, response['nextPageToken'])

        if response:
            email_list = get_emails_from_messages(response['datalist'])

            for k, v in email_list.items():
                if k in emails:
                    emails[k] += 1
                else:
                    emails[k] = 1

    reply_data = []

    for email, count in emails.items():

        if len(email) == 2:
            reply_data.append({'name': email[0], 'email': email[1], 'count': count})

    return sorted(reply_data, key=lambda k: k['count'], reverse=True)
