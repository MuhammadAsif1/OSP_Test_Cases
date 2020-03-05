import os
os.system("source /home/osp_admin/.env/bin/activate")
import sys
import json
from openstack import connection
import pdb
import time


"""
	SETTING ENVIRONMENT VARIABLE FOR R153
"""
class Source_Module():
    os.environ["OS_NO_CACHE"]="True"
    os.environ["COMPUTE_API_VERSION"]="1.1"
    os.environ["OS_USERNAME"]="admin"
    os.environ["no_proxy"]=",100.67.153.161,192.168.120.100"
    os.environ["OS_USER_DOMAIN_NAME"]="Default"
    os.environ["OS_VOLUME_API_VERSION"]="3"
    os.environ["OS_CLOUDNAME"]="r153"
    os.environ["OS_AUTH_URL"]="http://100.67.153.61:5000//v3"
    os.environ["NOVA_VERSION"]="1.1"
    os.environ["OS_IMAGE_API_VERSION"]="2"
    os.environ["OS_PASSWORD"]="fpJwYm9yqWNZXsfaANJFPcvwC"
    os.environ["OS_PROJECT_DOMAIN_NAME"]="Default"
    os.environ["OS_IDENTITY_API_VERSION"]="3"
    os.environ["OS_PROJECT_NAME"]="admin"
    os.environ["OS_AUTH_TYPE"]="password"