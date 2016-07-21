# Django Backblaze B2 Storage
A backblaze B2 storage system for django

## Description
django-b2storage is a storage system for django using the cloud service [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html "link to b2 website").

## Installation
To install django-b2storage:

```sh
$ pip install django_b2storage
```

Then in your settings file, add the following:
```sh
DEFAULT_FILE_STORAGE = 'django_b2storage.backblaze_b2.B2Storage'
B2_ACCOUNT_ID = 'your_account_id'
B2_APPLICATION_KEY = 'your_application_key'
B2_BUCKET_NAME = 'your_bucket_name'
B2_BUCKET_ID = 'your_bucket_id'
```

And That's It!!!
You will now be able to refer to user uploaded files using:
```sh
object_with_file.file.url()
```

## Tutorial
To see this in action alongside with [Heroku](https://www.heroku.com/ "link to heroku webite"), see my tutorial [here](http://example.com/ "link to my tutorial")
