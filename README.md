# Worker safety with GluonCV and Amazon Rekognition (Web Cam Version)

Use Laptop WebCam, GluonCV on MXNet and Amazon Rekognition to build an application that helps identify if a person at a construction site is wearing the right safety gear, in this case, a hard hat. 

## Learning objectives
In this lab you will learn the following:
- Create and deploy an object detection project to your local device.
- Modify object detection code so that it detect persons and upload the frame to Amazon S3.
- Create a Lambda function to identify persons who are not wearing safety hats.
- Analyze the results using AWS IoT , Amazon CloudWatch and a web dashboard.

## Architecture

![](arch.png)

Follow the modules below or refer to the online course to learn how to build the application in 30 minutes.

## Online course 

[![Online Course](worker-safety-sc.png)](https://www.aws.training/learningobject/wbc?id=32077)

https://www.aws.training/Details/eLearning?id=32077

## Modules

### Setup an AWS IAM role for a cloud Lambda function

1. Go to AWS IAM in AWS Console at https://console.aws.amazon.com/iam
2. Click on Roles
3. Click create role
4. Under AWS service, select Lambda and click Next: Permissions
5. Under Attach permission policies
    1. search for S3 and select AmazonS3FullAccess
    2. search for Rekognition and select checkbox next to AmazonRekognitionReadOnlyAccess
    3. search for cloudwatch and select checkbox next to CloudWatchLogsFullAccess and CloudWatchFullAccess
    4. search for iot and select AWSIotDataAccess
    5. search for lambda and select checkbox next to AWSLambdaFullAccess
6. Click Next: Tags and Next: Review
7. Name is “RecognizeObjectLambdaRole”
8. Click Create role


### Setup an AWS IAM user for Local Function

*Skip this step if you already have aws-cli access configured from your local machine*

1. Go to AWS IAM in AWS Console at https://console.aws.amazon.com/iam
2. Click on Users and then click Add user
3. In the Add User form
    1. Give your user a good user name like - your-name-worker-safety (example: adesojia-worker-safety)
    2. Click on Programmatric access on AWS access type
    3. Click Next: Permissions
4. Under Set permissions, select 'Attach existing policies directly' 
    1. Search for AmazonS3FullAccess and select it
    2. Click Next: Tags
5. Leave blank and go on to click Next:Review
6. On the review page ensure that AmazonS3FullAccess is listed under Permissions summary and click Create User
7. You should see a success screen. Take note of your Access Key ID and click to show your Secret key and take note of that as well. 
8. On your computer, open a terminal window and type `aws configure`. 
    If you do not have aws installed follow these [instructions](https://docs.amazonaws.cn/en_us/cli/latest/userguide/install-cliv1.html) to get aws-cli installed 
9. Enter the Access Key ID and Secret key from the previous step. For region leave the default and for output format leave the default.

### Create an Amazon S3 bucket

1. Go to Amazon S3 in AWS Console at https://s3.console.aws.amazon.com/s3/
2. Click on Create bucket.
3. Under Name and region:

* Bucket name: Enter a bucket name such as -> your name-worker-safety (example: kashif-worker-safety)
* Choose US East (N. Virginia)
* Click Next

4. Leave the default values for Configure Options but ensure that the S3 bucket is not blocking public access and click Next
5. Click Next, and click Create bucket.

### Create a cloud Lambda function

1. Go to Lambda in AWS Console at https://console.aws.amazon.com/lambda/
2. Click on Create function.
3. Under Create function, by default Author from scratch should be selected.
4. Under Author from scratch, provide the following details:

* Name: worker-safety-cloud
* Runtime: Python 3.7
* Role: Choose an existing role
* Existing role: RecognizeObjectLambdaRole
* Click Create function

1. Under Environment variables, add a variable:

* Key: iot_topic
* Value: worker-safety-demo-cloud

1. Copy the code from [cloud-lambda.py](./code/cloud-lambda.py) and paste it under the Function code for the Lambda function. 
2. Click Save.

1. Under Add triggers, select S3.
2. Under Configure triggers:

* Bucket: Select the S3 bucket you just created in earlier step.
* Event type: Leave default Object Created (All)
* Leave defaults for Prefix and Suffix and make sure Enable trigger checkbox is checked.
* Click Add.
* Click Save on the top right to save the changes to the Lambda function.

### Create an Object Detection inference function using MXNet and GluonCV

0. Run the following in a terminal or conda environment `pip install mxnet gluoncv`
1. Download the code from [demo-webcam.py](./code/demo_webcam.py) to your local machine. 
2. Go to line 18 and modify the line below with the name of your S3 bucket created in the earlier step.

* bucket_name = "REPLACE-WITH-NAME-OF-YOUR-S3-BUCKET"

3. Save the code and run it by going to the directory where it is saved and running `python demo_webcam.py`. This should trigger the webcam on your computer to start running and publishing images to s3 when it detects a person in the frame.

### View output in AWS IoT

1. Go to AWS IoT console at https://console.aws.amazon.com/iot/home and Click Test and Subscribe to a topic
2. Under Subscription topic, enter the topic name that you entered as an environment variable for the Lambda function you created in the earlier step (example: worker-safety-demo-cloud) and click Subscribe to topic.
3. You should now see JSON message with a list of people detected and whether they are wearing safety hats or not.

### View output in Amazon CloudWatch

* Go to Amazon CloudWatch Console at https://console.aws.amazon.com/cloudwatch
* Create a dashboard called “worker-safety-dashboard-your-name”
* Choose Line in the widget
* Under Custom Namespaces, select “string”, “Metrics with no dimensions”, and then select PersonsWithSafetyHat and PersonsWithoutSafetyHat.
* Next, set “Auto-refresh” to the smallest interval possible (1h), and change the “Period” to whatever works best for you (1 second or 5 seconds)

### View output in the web dashboard

1. Go to AWS Cognito console at https://console.aws.amazon.com/cognito
2. Click on Manage Identity Pools
3. Click on Create New Identity Pool
4. Enter “awsworkersafety” for Identity pool name
5. Select Enable access to unauthenticated identities
6. We are using Unauthenticated identity option to keep things simple in the demo. For real world applications where you only want authorized users to access the app, you should configure Authentication providers.
7. Click Create Pool
8. Expand View Details
9. Under: Your unauthenticated identities would like access to Cognito, expand View Policy Document and click Edit.
10. Click Ok for Edit Policy prompt.
11. Copy JSON from [cognitopolicy.json](./code/cognitopolicy.json) and paste in the text box.
12. Click Allow
13. Make a note of the Identity Pool as you will need it in the following steps.
14. Go to AWS IoT in AWS Console at: https://console.aws.amazon.com/iot
15. Click on settings and make a note of the endpoint, you will need this the following step.
16. Download [webdashboard.zip](./code/webdashboard.zip) and unzip on your local drive.
17. Edit aws-configuration.js and update poolId with Cognito Identity Pool Id and host with IoT EndPoint you got in the earlier steps.
18. From the terminal go to the root of the unzipped folder and run “npm install”
19. Next, run “./node_modules/.bin/webpack —config webpack.config.js”
20. This will create a build that we can easily deploy.
21. Go to Amazon S3 bucket, and create a folder titled "web"
22. From the web folder in S3 bucket, click upload and select bundle.js, index.html and style.css.
23. From Set permission, Choose Grant public read access to the objects. and click Next
24. Leave default settings for following screens and click Upload.
25. Click on index.html and click on the link to open the web page in browser.
26. In the address URL append ?iottopic=NAME-OF-YOUR-IOT-TOPIC. This is the same value you added to the Lambda environment variable and hit Enter.
27. You should now see images coming in from AWS DeepLens with a green or red box around the person. Green indicates the person is wearing a safety hat and red indicates a person who is not. 

This completes the application- you have now learnt to build an application that detects if a person at a construction site is wearing a safety hat or not. You can quickly extend this application to detect lab coats or boots etc. 

Before you exit, make sure you clean up any resources you created as part of this lab. 

## Clean up
Delete Lambda functions, S3 bucket and IAM roles.

## License Summary

This sample code is made available under the MIT-0 license. See the LICENSE file.
