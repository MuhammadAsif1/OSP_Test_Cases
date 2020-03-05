import commands
import os
import json
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import pdb
import sys
import time
#########################logger code start
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

############################## Variables that will be used 
pf_id=""
nic_id=""
aggregate_group_name="sriov"
compute_node="r153-dell-compute-0"
flavor="sriov_offload_flavor"
sriov_net_name="sriov_net"
physical_network_name="physint"
sriov_subnet_name="sriov_sub"
image_name="centos"
sriov_vm_name="sriov_vm"
sriov_port_id=""
availablity_zone="sriov"
global output=""
router="router1"
security_group="default-id"
##############################


def command_function(client,com):
   output=""
   stdin, stdout, stderr = client.exec_command(com)
   stdout=stdout.readlines()
   
   print("====================================================")
   for line in stdout:
       output=output+line
   if output!="":
       print output
   else:
       print "There was no output for this command"
   print("====================================================") 
########################################################################################
def Delete_function(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name):
   print("=================== Deleting an Aggregate Group ==================")
   os.system("openstack aggregate delete $aggregate_group_name")
   os.system("openstack port delete port1")
   print("==================== Deleting Subnet ===========================")
   os.system("openstack subnet delete $sriov_subnet_name")
   print("==================== Deleting SRIOV-enabled Network =======================")
   os.system("openstack network delete $sriov_net_name")
      
   print("==================== Creating instance ======================")
   os.system("openstack server delete $sriov_vm_name")
   print("===================================================================================================================")
##############################################################################################
def floating_ip(instance):
   os.system("openstack floating ip create $physical_network_name")
   #assign floating ip to instance
   print("================================= List of Floating Ips =====================")
   os.system("openstack floating ip list")
   Floating_IP=raw_input("Floating_IP : ")
   os.environ['Floating_IP'] = Floating_IP
   os.system("openstack server add floating ip $instance $Floating_IP")
   return Floating_IP


#########################################################################################
def verify_vfs_created_test_case_3():
   client_compute=paramiko.SSHClient()
   client_compute.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client_compute.connect('192.168.120.35', username='heat-admin', password="")
   output=""
   print("=============================================================== ")
   com="ip link show $pf_id"
   command_function(client_compute,com)
   client_compute.close()
################################################################################################   
def verify_pci_mode_test_case_5():
   client_compute=paramiko.SSHClient()
   client_compute.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client_compute.connect('192.168.120.35', username='heat-admin', password="")
   output=""
   print("=============================================================== ")
   com="devlink dev eswitch show pci $nic id"
   command_function(client_compute,com)
   client_compute.close()
################################################################################################
def verify_pci_mode_test_case_6():
   client_compute=paramiko.SSHClient()
   client_compute.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client_compute.connect('192.168.120.35', username='heat-admin', password="")
   output=""
   print("=============================================================== ")
   com="ovs-vsctl get Open_vSwitch"
   command_function(client_compute,com)
   client_compute.close()

def create_sriov_offload_enabled_instance_test_case_7(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name):
   try:
      print("=================== Creating an Aggregate Group ==================")
      os.system("openstack aggregate create --zone $availablity_zone $aggregate_group_name")
      print("=================== List the hosts available in your environment ==========")
      os.system("openstack host list")
      print("=================== Adding Compute node in Aggregate Group ==================")
      os.system("openstack add host $compute_node $aggregate_group_name")
      print("==================== Creating Flavor ====================================")
      os.system("openstack flavor create $flavor --ram 4096 disk 150 vcpu 2")
      os.system("openstack flavor set --property sriov=true --property hw:cpu_policy=dedicated --property hw:mem_page_size=1GB $flavor")
      print("==================== Creating SRIOV-enabled Network =======================")
      os.system("openstack network create --provider-network-type=vlan --provider-physical-network=$physical_network_name $sriov_net_name")
      print("==================== Creating Subnet ===========================")
      os.system("openstack subnet create --project admin --cidr 10.0.10.0/24 --dhcp --network $sriov_net_name --allocation-pool start=10.0.10.20,end=10.0.10.50 $sriov_subnet_name")
      
      print("========================== Creating Router and adding interface of Public Network =============================")
      os.system("openstack router create $router && openstack router set $router --external-gateway $physical_network_name")
      print("========================== Adding Public Subnet to Router =============================")
      os.system("openstack router add subnet $router $physical_network_name")
      print("========================== Creating Port in $network =============================")
      os.system("openstack port create --network $sriov_net_name --fixed-ip subnet=$sriov_subnet_name,ip-address=10.0.10.30 port1")
      os.system("openstack router add subnet $router $sriov_subnet_name")
      print("==================== Creating instance ======================")
      
      print("Creating key pair with the name of sriov_keypair.pem")
      os.system("openstack keypair create sriov_keypair >> sriov_keypair.pem")
      
      os.system("openstack server create --flavor $flavor --availability-zone $availablity_zone --$image_name --nic port-id=$sriov_port_id --security-group $security_group --key-name sriov_keypair $sriov_vm_name")�
      print("===================================================================================================================")
      if(os.system(openstack server show $sriov_vm_name | grep status)== "Active"):
         print("================= Test Case Completed Successfully ======================")
      else:
         print("================= Test Failed ========================")
         Delete_function(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name)
      print("===================================================================================================================")
   except:
      Delete_function(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name)
   
def verify_creation_of_representator_port_test_case_8():
   client_compute=paramiko.SSHClient()
   client_compute.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client_compute.connect('192.168.120.35', username='heat-admin', password="")
   output=""
   print("=============================================================== ")
   com="sudo -i && ovs-dpctl show"
   command_function(client_compute,com)
   client_compute.close()
   if(output==""):
      ###### we will compare here the output of this command that command because currently i dont know what will be the output ,, so can't say any thing about it
def on_different_compute_node_same_network():
   
   
   create_sriov_offload_enabled_instance_test_case_7(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name)
   Floating_IP1=floating_ip(sriov_vm_name)
   #parameter values for 2nd instance 
   pf_id=""
   nic id=""
   aggregate_group_name="sriov"
   compute_node="r153-dell-compute-1"
   flavor="sriov_offload_flavor"
   sriov_net_name="sriov_net"
   physical_network_name="physint"
   sriov_subnet_name="sriov_sub"
   image_name=""
   sriov_vm_name="sriov_vm"
   sriov_port_id=""
   availablity_zone="sriov"
   global output=""
   router="router1"
   create_sriov_offload_enabled_instance_test_case_7(availablity_zone,aggregate_group_name,compute_node,flavor,physical_network_name,sriov_net_name,sriov_subnet_name,router,image_name,sriov_port_id,sriov_vm_name)
   Floating_IP2=floating_ip(sriov_vm_name)
   ########
   os.system("ping IP1")
   os.system("ping IP2")
   client_instance=paramiko.SSHClient()
   client_instance.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client_instance.connect('IP1', username='heat-admin', password="")  # have to see how to ssh using keys through paramiko
   output=""
   print("=============================================================== ")
   com="ping IP2"
   command_function(client_instance,com)
   client_instance.close()
   
   
   