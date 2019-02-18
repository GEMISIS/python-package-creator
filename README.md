# python-package-creator
Got tired of having to spin up EC2 instances for creating python package archives for AWS Lambda, so here's a Lambda function to do so for me/you!

# Deploying
To deploy, first setup an S3 bucket and ensure that your Lambda function can upload public files with the ACL settings (Permissions -> Public access settings -> Disable both **'Block new public ACLs and uploading public objects (Recommended)'** and **'Remove public access granted through public ACLs (Recommended)'**). This ensures that you can make the files publically available. If you don't want them to be public, simply remove the **ExtraArgs** supplied to the **s3.upload_file** method in **lambda_function.py**.

Next, create a Lambda function and upload the zip archive of this repository to it. Add two environment variables: **bucket_name** with a value of the previously created S3 bucket's name, and **bucket_url** with a value of the URL that files can be downloaded from (can be gibberish if you disabled public downloads previously). Next, make sure your IAM Role for this Lambda function has permission to use the **PutObject** and **PutObjectAcl** Actions on your S3 bucket (you only need the **PutObject** permission if you don't allow public uploads). Finally, add an API Gateway trigger to your Lambda function and ensure that it allows POST requests to your Lambda function.

You should finally be all set to go!

# Testing
You can test your setup by doing the following from a terminal window:
```
curl -d '{"packages": ["Pillow"]}' -H "Content-Type: application/json" -X POST lambda_endpoint
```
Make sure to replace **lambda_endpoint** with your Lambda's endpoint.