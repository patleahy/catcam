from subprocess import call
from datetime import datetime
from time import sleep
from sys import argv
import os.path
import boto3
import botocore


def main(bucket, prefix):
    """
    Take a picture, copy it to an s3 bucket and put a img tag in a html file in the s3 bucket.

    bucket  the name of the bucket
    prefix  the path in the bucket to put the image
    """

    now = datetime.now()
    
    upload_folder = './upload/{:0000}/{:00}/{:00}'.format(now.year, now.month, now.day)
    make_folder(upload_folder)
    
    filename = '{:%Y-%m-%d-%H-%M.jpg}'.format(now)
    save_img(os.path.join(upload_folder, filename), 4)

    prefix = '{}/{:0000}/{:00}/{:00}/'.format(prefix, now.year, now.month, now.day)

    upload_file(bucket, prefix, upload_folder, filename)

    add_to_index(bucket, prefix, upload_folder, filename, now)


def make_folder(name):
    if not os.path.exists(name):
        log('Make dirs name={}', name)
        os.makedirs(name)


def save_img(filepath, trys):
    """
    Use the fswebcam command to take a picture.
    This command fails often so I retry it multiple times with a 60 second sleep between tries.

    filepath    where to save the file
    trys        how many times to try to save the file
    """
    
    
    file_saved = False
    i = 0

    while not file_saved and i < trys:
        log('Saving try={} filepath={}', i, filepath)
        call(['fswebcam', '--no-banner', '--resolution', '640x480', filepath])
        if os.path.isfile(filepath):
            log('File saved try={} filepath={}', i, filepath)
            return
        log('Sleeping try={} filepath={}', i, filepath)
        sleep(60)
        i += 1

    log('File not saved trys={} filepath={}', trys, filepath)
    raise Exception('File not saved filepath={}'.format(filepath))


def upload_file(bucket, prefix, upload_folder, filename):
    """
    Upload a file to s3

    bucket          the bucket to upload to
    prefix          the prefix path to upload the file into
    upload_folder   the folder containing the file
    filename        the name of the file to upload
    """

    filepath = os.path.join(upload_folder, filename)
    objectpath = os.path.join(prefix, filename)

    log('Upload filepath={} bucket={} objectpath={}', filepath, bucket, objectpath)

    s3 = boto3.client('s3')
    s3.upload_file(filepath, bucket, objectpath, ExtraArgs={
        'ACL': 'public-read',
        'StorageClass': 'STANDARD'})

    log('Uploaded filepath={} bucket={} objectpath={}', filepath, bucket, objectpath)


def add_to_index(bucket, prefix, upload_folder, filename, now):
    """
    Add an img tag for a file to the index.html file. If there is no index.html file then one is created. 
    
    This works by downloading the image.html file from s3. Finding the commet "<!-- INSERT_HERE -->" in the file.
    Add the new img tag just before the comment. And then uploading the updated file back to s3. If there is no
    existing file at s3 then the index.html file in the same folder as this script is used.

    bucket          the bucket to upload to
    prefix          the prefix path to upload the file into
    upload_folder   the folder containing the file
    filename        the name of the file to upload
    now             the date time used to set the title of the html file
    """
    
    s3 = boto3.client('s3')

    key = os.path.join(prefix, 'index.html')

    log('Check for file bucket={} key={}', bucket, key)
    obj = s3.list_objects(Bucket=bucket, Prefix=key)
    if obj.get('Contents'):
        log('Read file bucket={} key={}', bucket, key)
        text = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
    else:
        log('File not found bucket={} key={}', bucket, key)
        index_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'index.html')
        with open(index_file, 'r') as f:
            text = f.read() 
        text = text.format(time=now)

    insert_here_tag = '<!-- INSERT_HERE -->'

    line = '<p><img src="{}"></p><p>{:%H:%M}</p>{}'.format(filename, now, insert_here_tag)
    log('Append line={}'.format(line))

    text = text.replace(insert_here_tag, line)

    log('Upload index bucket={} key={}', bucket, key)
    s3.put_object(Bucket=bucket, Key=key, Body=text.encode('utf8'), 
        ContentType="text/html", ACL='public-read', StorageClass='STANDARD')

    log('Uploaded index bucket={} key={}', bucket, key)


def log(text, *args):
    text = text.format(*args)
    print('SNAP {} {}'.format(datetime.now(), text))


if __name__ == '__main__':
    main(argv[1], argv[2])
