import json

import quart
import quart_cors
import boto3 
import botocore
from quart import request
import os

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="*") #https://chat.openai.com")

class S3():
    def __init__(self):
        self.client = None
        if os.environ.get("AWS_ACCESS_KEY_ID") is not None and os.environ.get("AWS_SECRET_ACCESS_KEY") is not None:
            print("Found credentials in environment, authenticating...")
            self.authenticate(os.environ.get("AWS_ACCESS_KEY_ID"), os.environ.get("AWS_SECRET_ACCESS_KEY"))

    def authenticate(self, access_key_id, secret_access_key):
        self.client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

s3 = S3()

@app.post("/aws/authenticate")
async def authenticate():
    r = await request.get_json()
    s3.authenticate(r['access_key_id'], r['secret_access_key'])
    return quart.Response(response="OK", status=200)

@app.post("/aws/s3/create_bucket")
async def create_bucket():
    r = await request.get_json()
    try:
        if s3.client.create_bucket(Bucket=r['bucketName']):
            return quart.Response(response=json.dumps({'bucketName': r['bucketName']}, indent=4, sort_keys=True, default=str), status=200)
        else:
            return quart.Response(response=json.dumps({'bucketName': r['bucketName']}, indent=4, sort_keys=True, default=str), status=500)
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)

@app.get("/aws/s3/list_objects/<string:bucketName>")
async def list_bucket(bucketName):
    try:
        response = s3.client.list_objects(Bucket=bucketName)
        return quart.Response(response=json.dumps(response['Contents'], indent=4, sort_keys=True, default=str) if "Contents" in response else '[]', status=200)
        
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)

@app.get("/aws/s3/get_object/<string:bucket>&<string:key>")
async def get_object(bucket, key):
    try:
        response = s3.client.get_object(Bucket=bucket, Key=key)
        if "Body" in response:
            return quart.Response(response=json.dumps(str(response["Body"].read())), status = 200)
        else:
            return quart.Response(response="Object not found", status=200)
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)

@app.post("/com/amazonaws/s3/PutObjectRequest")
async def put_object():
    r = await request.get_json()
    try:
        s3.client.put_object(Bucket=r['com.amazonaws.s3#BucketName'], Key=r['com.amazonaws.s3#ObjectKey'], Body=r['com.amazonaws.s3#StreamingBlob'])
        return quart.Response(response='OK', status=200)
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)

# @app.post("/aws/s3/put_object")
# async def put_object():
#     r = await request.get_json()
#     try:
#         s3.client.put_object(Bucket=r['bucket'], Key=r['key'], Body=r['data'])
#         return quart.Response(response='OK', status=200)
#     except botocore.exceptions.ClientError as e:
#         return quart.Response(response=f'NOT OK: {e}', status=500)
    
@app.post("/aws/s3/delete_object")
async def delete_object():
    r = await request.get_json()
    try:
        s3.client.delete_object(Bucket=r['bucket'], Key=r['key'])
        return quart.Response(response='OK', status=200)
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)

@app.get("/logo.png")
async def plugin_logo():
    return await quart.send_file("logo.png", mimetype='image/png')


@app.get("/favicon.ico")
async def plugin_favicon():
    return await quart.send_file("favicon.ico", mimetype='image/png')


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    with open("ai-plugin.json") as f:        
        return quart.Response(f.read(), mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    with open("openapi.yaml") as f:
        return quart.Response(f.read(), mimetype="text/yaml")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
async def index(path):
    return quart.Response(response=json.dumps({'msg': 'catch all'}), mimetype="text/json")

if __name__ == '__main__':
    app.run()
