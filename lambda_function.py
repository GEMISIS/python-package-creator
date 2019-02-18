import base64
import boto3
import datetime
import json
import os
import pip._internal as pip
import random
import shutil
import string
import zipfile

def parse_request(event):
    packages = []
    try:
        # Check if we have a body object and use that first.
        if event is not None and 'body' in event:
            req = event['body']
            # Check if we need to decode it from a base64 string.
            if 'isBase64Encoded' in event and event['isBase64Encoded']:
                req = json.loads(base64.b64decode(req))

            # Get our outputs.
            packages = req['packages']
        else:
            # Otherwise we assume that the dictionary object contains
            # everything we need.
            packages = event['packages']
    except:
        pass

    return packages

def install(packages, id):
    for package in packages:
        try:
            pip.main(['install', package, '--target', '/tmp/{0}'.format(id)])
        except:
            return False
    return True

def archive_packages(path, zip):
    zip_archive = zipfile.ZipFile(zip, 'w')
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_archive.write(os.path.join(root, file))
    zip_archive.close()

def lambda_handler(event, context):
    # Generate a random string of characters to act as an ID for the request.
    # Packages should be deleted after 24 hours to prevent collisions. Still super hacky.
    id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))

    # Get list of packages.
    packages=parse_request(event)
    if len(packages) < 1:
        return {
            'statusCode': 200,
            'body': json.dumps('No packages chosen!')
        }
    
    # pip install each pacakge to the /tmp directory.
    if install(packages, id) == False:
        return {
            'statusCode': 200,
            'body': json.dumps('Error installing {0}'.format(', '.join(packages)))
        }

    # Create a zip archive of all of our packages.
    archive_packages('/tmp/{0}/'.format(id), '/tmp/{0}.zip'.format(id))

    # Upload the file to S3 next.
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/{0}.zip'.format(id), os.environ['bucket_name'], '{0}.zip'.format(id), ExtraArgs={
        'ACL':'public-read'})

    # Cleanup everything from our temporary folder.
    try:
        shutil.rmtree('/tmp/{0}'.format(id))
        os.remove('/tmp/{0}.zip'.format(id))

        # Return a link to our file for the user to click.
        return {
            'statusCode': 200,
            'body': json.dumps('{0}/{1}.zip'.format(os.environ['bucket_url'], id))
        }
    except:
        # If we couldn't delete the temporary file or zip archive we've
        # probably been unable to create them for some reason, meaning we should
        # error out.
        return {
            'statusCode': 200,
            'body': json.dumps('Error creating package archive!')
        }
