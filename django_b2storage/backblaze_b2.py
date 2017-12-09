import json
import mimetypes
import hashlib
import requests
import os

from urllib2 import Request, urlopen, quote

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from .connectioninfo import ConnectionInfo, encode



@deconstructible
class B2Storage(Storage):
    def __init__(self, *args, **kwargs):
        super(B2Storage, self).__init__(*args, **kwargs)
        self.connection = ConnectionInfo()


    def _open(self, name, mode="rb"):
        url = self.connection.download_url + "/file/" + self.connection.BUCKET_NAME + "/" + name
        headers = {
            'Authorization' : self.connection.auth_token
        }
        request = requests.post(url, data=None, headers=headers)
        response_data = json.loads(request.content)
        return ContentFile(response_data)

    def _save(self, name, content):
        name = os.path.basename(name)
        upload_data = self.connection.upload_data
        file_data = content.read()
        file_sha1 = hashlib.sha1(file_data).hexdigest()
        content_type = ""
        if hasattr(content.file, 'content_type'):
            content_type = content.file.content_type
        else:
            content_type = mimetypes.guess_type(name)[0]
        headers = {
            'Authorization' : quote(upload_data['authorizationToken'].encode('utf-8')),
            'X-Bz-File-Name' : quote(name.encode('utf-8')),
            'Content-Type' : quote(content_type.encode('utf-8')),
            'X-Bz-Content-Sha1' : quote(file_sha1.encode('utf-8')),
        }
        request = requests.post(upload_data['uploadUrl'], data = file_data, headers = headers)
        response_data = json.loads(request.content)
        # Add file_name:file_id to our dict
        file_id = response_data['fileId']
        name = response_data['fileName']
        self.connection.name_id_dict[name] = file_id
        return name


    def delete(self, name):
        file_id = self.connection.get_file_id(name)
        request = requests.post(
            '%s/b2api/v1/b2_delete_file_version' % self.connection.api_url,
            data = encode(json.dumps({ 'fileName' : name, 'fileId' : file_id })),
            headers = { 'Authorization': self.connection.auth_token }
        )
        json.loads(request.content)
        del self.connection.name_id_dict[name]

    def url(self, name):
        return self.connection.download_url + '/file/' + self.connection.BUCKET_NAME + '/' + name


    def exists(self, name):
        return name in self.connection.name_id_dict
