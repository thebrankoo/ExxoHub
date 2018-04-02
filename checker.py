"""This module process location data."""
import json
import requests
import LocationStorage
# import boto3
# from botocore.exceptions import ClientError

URL_PRE = "https://exxo:exxopass123@"

SAVER = LocationStorage.Saver()

class Notifier(object):
    '''sends email notifications'''
    username = ""
    password = ""

    def __init__(self, username = "", password = ""):
        self.username = username
        self.password = password

#    def send_email(self, send_to, email_text):
#         '''sends an email'''
#         sender = "exxotechnologies@gmail.com"
#         recipient = "bne.rca@gmail.com"
#         aws_region = "eu-west-1"
#         subject = "Location update"
#         char_set = "UTF-8"
#         client = boto3.client('ses', region_name=aws_region)

#         try:
#             #Provide the contents of the email.
#             response = client.send_email(
#                 Destination={
#                     'ToAddresses': [
#                     recipient,
#                     ],
#                 },
#                 Message={
#                     'Body': {
#                         'Html': {
#                             'Charset': char_set,
#                             'Data': email_text,
#                         },
#                         'Text': {
#                             'Charset': char_set,
#                             'Data': email_text,
#                         },
#                     },
#                     'Subject': {
#                         'Charset': char_set,
#                         'Data': subject,
#                     },
#                 },
#                 Source=sender,
#             )
# # Display an error if something goes wrong.
#         except ClientError as e:
#             print(e.response['Error']['Message'])
#         else:
#             print("Email sent! Message ID:"),
#             print(response['ResponseMetadata']['RequestId'])

class LocationRequester(object):
    """This class fetches and parses santinel location data."""
    target_url = ""

    base_download_url = ""
    base_preview_url = ""
    location_summary = ""
    product_id = ""
    product_title = ""

    def __init__(self, requestURL):
        self.target_url = requestURL

    def goo_shorten_url(self, url):
        #return url
        api_key = "AIzaSyDS6tMQdPf4knUMU3QCwFEdxDMsXkLg8sc"
        req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
        payload = {'longUrl': url}
        headers = {'content-type': 'application/json'}
        r = requests.post(req_url, json=payload, headers=headers)
        resp = json.loads(r.text)
        return resp['id']

    def check_location(self):
        '''Checks location update and sends a notification'''
        parsed_message = self.parse_request_json()
        if not parsed_message:
            return False

    def request_location(self):
        """request_location(self) -> requests location satellite images as json"""
        response = requests.get(self.target_url)
        return response.json()

    def parse_request_json(self):
        """parse_request_json(self) - parses json form url and returns in mail format"""
        mail_text = ""

        json_data = self.request_location()
        json_encoded = json.dumps(json_data)
        json_decoded = json.loads(json_encoded)

        for value in json_decoded["feed"]["entry"]:
            self.product_title = value["title"]
            self.location_summary = value["summary"]
            self.product_id = value["id"]
            if SAVER.insert_location_info(self.product_id) == False:
                return False

            for lst in value['link']:
                if "rel" in lst:
                    if lst["rel"] == "alternative":
                        self.base_preview_url = lst["href"] + "/Products('Quicklook')/$value"
                        self.base_download_url = lst["href"] + "/$value"

                        download_url = URL_PRE + self.base_download_url[8:]
                        shortDownload = self.goo_shorten_url(download_url)

                        if self.base_preview_url == "":
                            shortPreview = "Preview is not available"
                        else:    
                            preview_url = URL_PRE + self.base_preview_url[8:]
                            shortPreview = self.goo_shorten_url(preview_url)

                        loc_summary_text = "Location summary: " + self.location_summary + "\n"
                        loc_preview_text = "Access location preview: " + shortPreview + "\n"
                        loc_url_text = "Download location: " + shortDownload + "\n"
                        mail_text += loc_summary_text + loc_preview_text + loc_url_text
                        mail_text += "=================================\n"

        return mail_text

URL_BASE = "scihub.copernicus.eu/dhus/search?"
URL_PARAMS1 = 'q=(platformname:Sentinel-2)'
URL_PARAMS2 = '%20AND%20footprint:"Intersects'
URL_PARAMS3 = '(POLYGON((19.83%2043.27,21.66%2043.29,21.64%2042.65,20.45%2042.67,19.83%2043.27)))"'
URL_PARAMS4 = '&format=json'

URL_FULL = URL_PRE + URL_BASE + URL_PARAMS1 + URL_PARAMS2 + URL_PARAMS3 + URL_PARAMS4
LOC_REQ = LocationRequester(URL_FULL)

MAIL = LOC_REQ.parse_request_json() 
print MAIL
# if MAIL != False:
#     print "Sending email"
#     Notifier().send_email(MAIL, "bne.rca@gmail.com")

# SAVER.fetch_lastest_loc_id()
# SAVER.remove_all_files()

