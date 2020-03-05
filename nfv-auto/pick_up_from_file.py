import pdb
import os

#pdb.set_trace()
if os.path.exists("/home/stack/overcloudrc"):
    with open('/home/stack/overcloudrc') as data_file:
        rc_file_cred = data_file.read()
    for line in rc_file_cred.split("\n"):
        if "OS_AUTH_URL" in str(line):
            os_auth_url = str(line.split("=")[1].strip())
        elif "OS_PASSWORD" in str(line):
            os_pass = str(line.split("=")[1].strip())
        elif "OS_PROJECT_NAME" in str(line):
            os_project_name = str(line.split("=")[1].strip())
        elif "OS_USERNAME" in str(line):
            os_username = str(line.split("=")[1].strip())
        elif "OS_PROJECT_DOMAIN_NAME" in str(line):
            os_domain_name = str(line.split("=")[1].strip())
else:
    print ("\nFAILURE!!! /home/stack/overcloudrc file not found!!!\nUnable to execute script\n\n")


pdb.set_trace()