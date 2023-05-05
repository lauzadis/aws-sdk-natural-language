# aws-sdk-natural-language

A ChatGPT plugin that enables you to use AWS with natural language.

Note: This is **not** an AWS product. This is an open source project enabling ChatGPT to *use* AWS.

## Architecture
![Architecture of the AWS SDK for Natural Language](./ai-plugin.png)

## Instructions
To run this yourself, you will need access to [ChatGPT plugins](https://openai.com/blog/chatgpt-plugins). 

Clone the repository and run `vercel`. Configure the deployment to your `vercel` account.

After it's deployed, go to ChatGPT and select the "Plugins" dropdown. Go to "Plugin store" --> "Develop your own plugin" and paste the URL of the Vercel deployment.

Start a new chat and enable the plugin you've just installed. First, you must provide your credentials to the plugin. After that, you can start making requests. Note [only a few operations are supported](#future) at this time.

 Note as of 04/30/23 the plugin URL is required to be HTTPS. If that requirement ever becomes less strict, you could run the server locally using `python ./api/index.py` and point ChatGPT to `localhost:5000` instead of the Vercel deployment.

## Sample Discussion

### Creating a bucket and uploading an object

**Human**: Access Key ID: **REDACTED**
Secret Access Key: **REDACTED**

**ChatGPT**: Great! I am now authenticated with your AWS account. How can I assist you with AWS services today?

**Human**: Can you make a bucket "matas-plugin-test-bucket"

**ChatGPT**: The S3 bucket "matas-plugin-test-bucket" has been successfully created. Is there anything else you would like me to do with AWS services?

**Human**: Can you tell me the number of objects currently in that bucket

**ChatGPT**: The S3 bucket "matas-plugin-test-bucket" currently contains 0 objects. Is there anything else you would like me to do with AWS services?

**Human**: Can you Base64 encode the text "Hello, ChatGPT!" and upload that to the bucket with the key "hello-chatgpt"

**ChatGPT**: The text "Hello, ChatGPT!" has been successfully Base64 encoded and uploaded to the S3 bucket "matas-plugin-test-bucket" with the key "hello-chatgpt". Is there anything else you would like me to do with AWS services?

**Human**: What is the number of objects in the bucket now?

**ChatGPT**: The S3 bucket "matas-plugin-test-bucket" currently contains 1 object with the key "hello-chatgpt". Is there anything else you would like me to do with AWS services?

**Human**: Can you get that object and display the contents?

**ChatGPT**: The content of the object with the key "hello-chatgpt" in the S3 bucket "matas-plugin-test-bucket" is "Hello, ChatGPT!". Is there anything else you would like me to do with AWS services?

## Future

Currently only a handful of S3 operations are supported:
- CreateBucket
- ListObjects
- PutObject
- GetObject
- DeleteObject

In the near future I plan to support every AWS service by code-generating `ai-plugin.json`, `openapi.yaml`, and the Flask server. 
