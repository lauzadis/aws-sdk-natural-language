import json

import quart
import quart_cors
import boto3 
import botocore

# Note: Setting CORS to allow chat.openapi.com is required for ChatGPT to access your plugin
app = quart_cors.cors(quart.Quart(__name__), allow_origin="*") #https://chat.openai.com")

class S3():
    def __init__(self):
        self.client = None

    def authenticate(self, access_key_id, secret_access_key):
        self.client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

s3 = S3()

@app.post("/aws/authenticate/<string:access_key_id>&<string:secret_access_key>")
async def authenticate(access_key_id, secret_access_key):
    s3.authenticate(access_key_id, secret_access_key)
    return quart.Response(response="OK", status=200)

@app.post("/aws/s3/create_bucket/<string:bucketName>")
async def create_bucket(bucketName):
    try:
        if s3.client.create_bucket(Bucket=bucketName):
            return quart.Response(response=json.dumps({bucketName: bucketName}, indent=4, sort_keys=True, default=str), status=200)
        else:
            return quart.Response(response=json.dumps({bucketName: bucketName}, indent=4, sort_keys=True, default=str), status=500)
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

@app.post("/aws/s3/put_object/<string:bucket>&<string:key>&<string:data>")
async def put_object(bucket, key, data):
    try:
        s3.client.put_object(Bucket=bucket, Key=key, Body=data)
        return quart.Response(response='OK', status=200)
    except botocore.exceptions.ClientError as e:
        return quart.Response(response=f'NOT OK: {e}', status=500)
    
@app.post("/aws/s3/delete_object/<string:bucket>&<string:key>")
async def delete_object(bucket, key):
    try:
        s3.client.delete_object(Bucket=bucket, Key=key)
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
