import json
import mimetypes
import hashlib
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from .connectioninfo import ConnectionInfo, decode, encode


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
        request = Request(url, None, headers)
        response = urlopen(request)
        response_data = json.loads(decode(response.read()))
        response.close()
        return ContentFile(response_data)

    def _save(self, name, content):
        upload_data = self.connection.upload_data
        file_data = content.read()
        file_sha1 = hashlib.sha1(file_data).hexdigest()
        content_type = ""
        if hasattr(content.file, 'content_type'):
            content_type = content.file.content_type
        else:
            content_type = mimetypes.guess_type(name)[0]
        headers = {
            'Authorization' : upload_data['authorizationToken'],
            'X-Bz-File-Name' :  name,
            'Content-Type' : content_type,
            'X-Bz-Content-Sha1' : file_sha1
        }
        request = Request(upload_data['uploadUrl'], file_data, headers)
        response = urlopen(request)
        response_data = json.loads(decode(response.read()))
        # Add file_name:file_id to our dict
        file_id = response_data['fileId']
        name = response_data['fileName']
        self.connection.name_id_dict[name] = file_id
        response.close()
        return name


    def delete(self, name):
        file_id = self.connection.get_file_id(name)
        request = Request(
            '%s/b2api/v1/b2_delete_file_version' % self.connection.api_url,
            encode(json.dumps({ 'fileName' : name, 'fileId' : file_id })),
            headers = { 'Authorization': self.connection.auth_token }
        )
        response = urlopen(request)
        json.loads(decode(response.read()))
        response.close()
        del self.connection.name_id_dict[name]

    def url(self, name):
        return self.connection.download_url + '/file/' + self.connection.BUCKET_NAME + '/' + name


    def exists(self, name):
        return name in self.connection.name_id_dict
