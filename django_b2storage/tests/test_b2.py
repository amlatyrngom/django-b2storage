import json
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from django.conf import settings
from django.core.files.base import ContentFile

from .b2settings import B2TestSettings

from . import mocks
from django_b2storage.backblaze_b2 import B2Storage, encode, decode, ConnectionInfo


class B2Test(unittest.TestCase):

    def setUp(self):
        self.storage = B2Storage()

    @patch("django_b2storage.backblaze_b2.Request")
    @patch("django_b2storage.backblaze_b2.ConnectionInfo.upload_data", new_callable=PropertyMock)
    @patch("django_b2storage.backblaze_b2.ConnectionInfo.auth_data", new_callable=PropertyMock)
    @patch("django_b2storage.backblaze_b2.urlopen")
    def test_save(self, mock_urlopen, mock_auth_data, mock_upload_data, mock_Request):
        mock_Request.return_value = "Request Result"
        mock_urlopen.return_value = mocks.MockUploadFileHttpResponse()
        mock_auth_data.return_value = mocks.mock_auth_data
        mock_upload_data.return_value = mocks.mock_upload_data
        self.storage.save('whatev.txt', ContentFile(b'Testing'))
        self.assertEqual(self.storage.connection.name_id_dict, {'test.txt' : 'my_file_id'})
        mock_urlopen.assert_called_with("Request Result")


    @patch("django_b2storage.backblaze_b2.Request")
    @patch("django_b2storage.backblaze_b2.ConnectionInfo.auth_data", new_callable=PropertyMock)
    @patch("django_b2storage.backblaze_b2.urlopen")
    def test_delete(self, mock_urlopen, mock_auth_data, mock_Request):
        # Insert one file in dict
        self.storage.connection.name_id_dict = {'test.txt' : 'my_file_id'}
        # Delete the File
        mock_Request.return_value = "Request Result"
        mock_urlopen.return_value = mocks.MockUploadFileHttpResponse() # Could be anything
        mock_auth_data.return_value = mocks.mock_auth_data
        self.storage.delete('test.txt')
        self.assertEqual(self.storage.connection.name_id_dict, {})
        mock_urlopen.assert_called_with('Request Result')


    @patch("django_b2storage.backblaze_b2.Request")
    @patch("django_b2storage.backblaze_b2.ConnectionInfo.auth_data", new_callable=PropertyMock)
    @patch("django_b2storage.backblaze_b2.urlopen")
    def test_open(self, mock_urlopen, mock_auth_data, mock_Request):
        mock_auth_data.return_value = mocks.mock_auth_data
        mock_Request.return_value = "Request Result"
        mock_urlopen.return_value = mocks.MockDownloadHttpResponse()
        my_file = self.storage.open("whatev.er")
        self.assertIsInstance(my_file, ContentFile)
        content = my_file.read()
        my_file.close()
        self.assertEqual(content, mocks.download_msg)


    @patch("django_b2storage.backblaze_b2.Request")
    @patch("django_b2storage.backblaze_b2.ConnectionInfo.auth_data", new_callable=PropertyMock)
    @patch("django_b2storage.backblaze_b2.urlopen")
    def test_exists(self, mock_urlopen, mock_auth_data, mock_Request):
        self.assertEqual(self.storage.exists('test.txt'), False)
        self.storage.connection.name_id_dict = {'test.txt' : 'my_file_id'}
        self.assertEqual(self.storage.exists('test.txt'), True)


    @patch("django_b2storage.backblaze_b2.ConnectionInfo.auth_data", new_callable=PropertyMock)
    def test_url(self, mock_auth_data):
        mock_auth_data.return_value = mocks.mock_auth_data
        self.assertEqual(self.storage.url('test.txt'), mocks.mock_auth_data['downloadUrl'] + '/file/' + settings.B2_BUCKET_NAME + '/test.txt')
