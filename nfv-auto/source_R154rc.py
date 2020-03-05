import os
os.system("source /home/osp_admin/.env/bin/activate")
import sys
import json
from openstack import connection
import pdb
import time


"""
	SETTING ENVIRONMENT VARIABLE FOR R154
"""
class Source_Module():
    os.environ["OS_NO_CACHE"]="True"
    os.environ["COMPUTE_API_VERSION"]="1.1"
    os.environ["OS_USERNAME"]="admin"
    os.environ["no_proxy"]=",100.67.154.160,192.168.120.251"
    os.environ["OS_USER_DOMAIN_NAME"]="Default"
    os.environ["OS_VOLUME_API_VERSION"]="3"
    os.environ["OS_CLOUDNAME"]="r154"
    os.environ["OS_AUTH_URL"]="http://100.67.154.160:5000//v3"
    os.environ["NOVA_VERSION"]="1.1"
    os.environ["OS_IMAGE_API_VERSION"]="2"
    os.environ["OS_PASSWORD"]="j6sERPagv3TdWaCGZxPz68cqb"
    os.environ["OS_PROJECT_DOMAIN_NAME"]="Default"
    os.environ["OS_IDENTITY_API_VERSION"]="3"
    os.environ["OS_PROJECT_NAME"]="admin"
    os.environ["OS_AUTH_TYPE"]="password"