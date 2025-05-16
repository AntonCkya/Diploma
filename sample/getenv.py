import os
from dotenv import load_dotenv

def get_dotenv_vars():
    # когда писал еще не знал о pydantic_settings
    load_dotenv()
    vars = {}
    vars['S3_BUCKET'] = os.getenv('S3_BUCKET')
    vars['S3_ENDPOINT_URL'] = os.getenv('S3_ENDPOINT_URL')
    vars['region'] = os.getenv('region')
    vars['aws_access_key_id'] = os.getenv('aws_access_key_id')
    vars['aws_secret_access_key'] = os.getenv('aws_secret_access_key')
    return vars
