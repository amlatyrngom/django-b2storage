import base64
import json
from urllib.request import Request, urlopen
import datetime

from django.conf import settings

def decode(m):
    return m.decode('utf-8')

def encode(m):
    return m.encode('utf-8')


class ConnectionInfo():
    """
    A class that contains information required to establish connections to the api
    """
    ACCOUNT_ID = settings.B2_ACCOUNT_ID
    APP_KEY = settings.B2_APPLICATION_KEY
    BUCKET_NAME = settings.B2_BUCKET_NAME
    BUCKET_ID = settings.B2_BUCKET_ID
    _validDuration = datetime.timedelta(days=1) # duration of the authorization token


    def __init__(self):
        self._auth_request_time = datetime.datetime.now() - 42*self._validDuration
        self._auth_data = dict()
        self.name_id_dict = dict() # To make get_file_id faster at the cost of memory


    @property
    def auth_data(self):
        """
        Returns the authorization data after sending a request with ID and APP_KEY. Updates the authorization token if necessary
        """
        # Check if the token is still valid
        if datetime.datetime.now() - self._auth_request_time >= self._validDuration:
            self._auth_request_time = datetime.datetime.now() # reset time
            id_and_key = self.ACCOUNT_ID + ':' + self.APP_KEY
            basic_auth_string = 'Basic ' + decode(base64.b64encode(id_and_key.encode('utf-8')))
            headers = {'Authorization' : basic_auth_string}
            request = Request(
                'https://api.backblaze.com/b2api/v1/b2_authorize_account',
                headers = headers
            )
            response = urlopen(request)
            self._auth_data = json.loads(decode(response.read()))
            response.close()
        return self._auth_data

    @property
    def auth_token(self):
        return self.auth_data['authorizationToken']

    @property
    def api_url(self):
        return self.auth_data['apiUrl']

    @property
    def download_url(self):
        return self.auth_data['downloadUrl']

    @property
    def minimumPartSize(self):
        return self.auth_data['downloadUrl']

    @property
    def upload_data(self):
        """
        Returns information needed for uploads given BUCKET_ID and authorization data.
        Since every upload can potentially fail, we need to resend Request every time.
        """
        request = Request(
            '%s/b2api/v1/b2_get_upload_url' % self.api_url,
            encode(json.dumps({ 'bucketId' : self.BUCKET_ID })),
            headers = { 'Authorization': self.auth_token }
        )
        response = urlopen(request)
        _upload_data = json.loads(decode(response.read()))
        response.close()
        return _upload_data

    def get_file_id(self, name):
        """
        Returns the id of the file.
        Looking for way to do it more efficiently(without downloading the file!)
        """
        return self.name_id_dict[name]
