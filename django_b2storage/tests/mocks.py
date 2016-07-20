import json
from django.conf import settings
from django.core.files.base import ContentFile

from .b2settings import B2TestSettings

settings.configure(**B2TestSettings)

from ..backblaze_b2 import B2Storage, encode, decode, ConnectionInfo


mock_upload_data = {
    "bucketId" : settings.B2_BUCKET_ID,
    "uploadUrl" : "https://wwww.uploadurl.com",
    "authorizationToken" : "3773"
}

mock_auth_data = {
    'authorizationToken' : '3773',
    'apiUrl' : 'https://wwww.api.com',
    'downloadUrl' : 'https://www.download.com',
    'minimumPartSize' : 733773377373,
}


mock_upload_file_data = {
    "fileId" : "my_file_id",
    "fileName" : "test.txt",
    "accountId" : settings.B2_ACCOUNT_ID,
    "bucketId" : settings.B2_BUCKET_ID,
    "contentLength" : 73,
    "contentSha1" : "bae5ed658ab3546aee12f23f36392f35dba1ebdd",
    "contentType" : "text/plain",
    "fileInfo" : {
       "author" : "unknown"
    }
}

download_msg = "Downloaded Successfully"

class MockUploadUrlHttpResponse():
    def read(self):
        return encode(json.dumps(mock_upload_data))

    def close(self):
        return None


class MockUploadFileHttpResponse():
    def read(self):
        return encode(json.dumps(mock_upload_file_data))

    def close(self):
        return None

class MockAuthHttpResponse():
    def read(self):
        return encode(json.dumps(mock_auth_data))

    def close(self):
        return None


class MockDownloadHttpResponse():
    def read(self):
        return encode(json.dumps(download_msg))

    def close(self):
        return None
