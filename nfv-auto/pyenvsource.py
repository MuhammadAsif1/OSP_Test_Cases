#!/home/osp_admin/.env/bin/active
import virtualenv
import pip
import os
import sys
import json
from openstack import connection
import pdb
import time


# class Source_Virtualenv():
env_dir = ".env"
file_exits=" "
file_exits=os.system("ls -a | grep .env")
print file_exits
# pdb.set_trace()
if file_exits == 1:
    print "create and activate the virtual environment"
    venv_dir = os.path.join(os.path.expanduser("~"), ".env")
    virtualenv.create_environment(venv_dir)
    execfile(os.path.join(venv_dir, "bin", "activate_this.py"))
    # pip install a package using the venv as a prefix
    # pip.main(["install", "--prefix", venv_dir, "xmltodict"])
else:
    print "activate the virtual environment"
    venv_dir = os.path.join(os.path.expanduser("~"), ".env")
    execfile(os.path.join(venv_dir, "bin", "activate_this.py"))
    os.system("pip freeze | grep openstacksdk")



    # pip install a package using the venv as a prefix
    # pip.main(["install", "--prefix", venv_dir, "xmltodict"])

    # import xmltodict
