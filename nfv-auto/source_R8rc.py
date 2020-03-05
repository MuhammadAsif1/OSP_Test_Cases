import os
import sys
import json
from openstack import connection
import pdb
import time


"""
	SETTING ENVIRONMENT VARIABLE FOR R8-14g
"""
class Source_Module():
    os.environ["OS_NO_CACHE"]="True"
    os.environ["COMPUTE_API_VERSION"]="1.1"
    os.environ["OS_USERNAME"]="admin"
    os.environ["no_proxy"]=",100.82.39.60,192.168.120.251"
    os.environ["OS_USER_DOMAIN_NAME"]="Default"
    os.environ["OS_VOLUME_API_VERSION"]="3"
    os.environ["OS_CLOUDNAME"]="r8-14g"
    os.environ["OS_AUTH_URL"]="http://100.82.39.60:5000//v3"
    os.environ["NOVA_VERSION"]="1.1"
    os.environ["OS_IMAGE_API_VERSION"]="2"
    os.environ["OS_PASSWORD"]="98Nzkx6UbaYsvNVAykvmffe6N"
    os.environ["OS_PROJECT_DOMAIN_NAME"]="Default"
    os.environ["OS_IDENTITY_API_VERSION"]="3"
    os.environ["OS_PROJECT_NAME"]="admin"
    os.environ["OS_AUTH_TYPE"]="password"