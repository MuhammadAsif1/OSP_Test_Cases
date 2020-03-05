#!/usr/bin/python
import commands
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules
from delete_os import Os_Deletion_Modules
import iperf3_funcs
import pdb
import time
import openstack
import sys

ssh_obj = ssh_functions()
creation_object = Os_Creation_Modules()
delete_object = Os_Deletion_Modules()

conn_create = creation_object.os_connection_creation()
conn_delete = delete_object.os_connection_creation()


def testing():
    ssh_obj.ssh_to("192.168.24.11","heat-admin")
    res = ssh_obj.execute_command_show_output("sudo ip netns exec qdhcp-981447b7-95c9-40f7-81b3-5202144f2aea timeout 10 tcpdump -i tap7b2e6cbe-24")
                                              #key.pem centos@192.168.40.16 \"timeout 10 tcpdump -i eth0\"")
    print res
    ssh_obj.ssh_close()


testing()