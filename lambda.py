''' Serialize Image Data lambda function'''

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # TODO implement
    ''''A function to serialize target data from s3'''
    
    s3 = boto3.client('s3')
    
    #get the s3 address from the step function event input
    key = event['s3_key']
    bucket = event['s3_bucket']
    
    #Dowload the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key, "/tmp/image.png")
    
    #we read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())
        
    #pass the data back to the step function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data" : image_data,
            "s3_bucket" : bucket,
            "s3_key" : key,
            "inferences" : []
            }
            
    }



''' Image Classifier lambda function '''
import json
import os
import boto3
import io
import base64

#setting the environment variables
ENDPOINT = "image-classification-2023-11-05-18-54-35-999"

#we will be using AWS's lightweight runtime solution to invoke and endpoint
runtime = boto3.Session().client('sagemaker-runtime')


def lambda_handler(event, context):
    # TODO implement
    
    #Decode the image data
    image = base64.b64decode(event["body"]["image_data"])
    
    #make a prediction
    response = runtime.invoke_endpoint(EndpointName = ENDPOINT, ContentType = "image/png", Body = image)
    
    predictions = json.loads(response['Body'].read().decode())
    
    #We return the data back to the step functions 
    event["body"]["inferences"] = predictions
    return {
        'statusCode': 200,
        'body': event
    }

''' Inference thresholf filter lambda function'''


import json

THRESHOLD = .90


def lambda_handler(event, context):
    # TODO implement
    
    #Grab the inferences from the event
    inferences = event['body']['body']['inferences']
    
    #checks if any vakues in our inference are above threshold
    meets_threshold = (max(inferences) > THRESHOLD)
    
    #If our threshold is met, pass our data back out of the step functions, else, end the step function with an error
    if meets_threshold:
        pass
    else:
        raise('Threshold_confidence_not_met')
    
    return {
        'statusCode': 200,
        'body': event
    }
