import paramiko
import string
import os
global client
global public_network
global instance
"""client=paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('192.168.10.111', username='root', password='xflow@123')
def command_function(com):
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
   """
#####################################End of function
###Test Case ######Check either barbican is enabled or disable ################
"""com="cd /home/osp_admin;python remote_script.py"
command_function(com)"""

#################################################
"""def test_secret():
   os.system("source ~/overcloud && openstack secret store --name testSecret --payload TestPayload")   
   os.system("source ~/overcloud && openstack secret list")"""
#################################################
def launch_instance():
   network=raw_input("Network Name : ")
   os.environ['network'] = network
   subnet=raw_input("Subnet Name : ")
   os.environ['subnet'] = subnet
   router=raw_input("Router Name : ")
   os.environ['router'] = router
   public_network=raw_input("Public Network Name : ")
   os.environ['public_network'] = public_network
   public_subnet=raw_input("Public Subnet Name : ")
   os.environ['public_subnet'] = public_subnet
   print("========================== Creating Network =============================")
   os.system("openstack network create $network")
   print("========================== Creating Subnet =============================")
   os.system("openstack subnet create $subnet --network $network --subnet-range 192.168.50.0/24")
   print("========================== Creating Router and adding interface of Public Network =============================")
   os.system("openstack router create $router && openstack router set $router --external-gateway $public_network")
   print("========================== Adding Public Subnet to Router =============================")
   os.system("openstack router add subnet $router $public_subnet")
   print("========================== Creating Port in $network =============================")
   os.system("openstack port create --network $network --fixed-ip subnet=$subnet,ip-address=192.168.50.40 port1")
   os.system("openstack router add subnet $router $subnet")
   #Creating a Instance
   flavor=raw_input("Flavor Name : ")
   os.environ['flavor'] = flavor
   print("========================== Creating Flavor =============================")
   os.system("openstack flavor create --id auto --ram 4096 --disk 25 --vcpus 2 --public $flavor")
   #Creating Barbican image
   file=raw_input("Cloud file to create image : ")
   os.environ['file'] = file
   os.system("ls")
   image=raw_input("Image Name : ")
   os.environ['image'] = image
   print("========================== Creating Image =============================")
   os.system("openstack image create --disk-format qcow2 --container-format bare --public --file $file $image")
   #creating Keypair
   print("Creating key pair with the name of barbican_keypair.pem")
   os.system("openstack keypair create barbican_keypair >> barbican_keypair.pem")
   #creating server
   print("========================= List of Available security Groups=================")
   os.system("openstack security group list")
   group=raw_input("security group : ")
   os.environ['group'] = group
   instance=raw_input("instance Name : ")
   os.environ['instance'] = instance
   os.system("openstack server create --flavor $flavor --image $image --key-name barbican_keypair --security-group $group --network $network $instance")
#################################################################
"""def floating_ip():
   os.system("openstack floating ip create $public_network")
   #assign floating ip to instance
   Floating_IP=raw_input("Floating_IP : ")
   os.environ['Floating_IP'] = Floating_IP
   os.system("openstack server add floating ip $instance $Floating_IP")
   #####################################ssh into instance######################
   client1=paramiko.SSHClient()
   client1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   client1.connect('192.168.10.111', username='root', password='xflow@123')
   output=""
   com="ping 8.8.8.8"
   stdin, stdout, stderr = client.exec_command(com)
   stdout=stdout.readlines()
   
   print("====================================================")
   for line in stdout:
       output=output+line
   if output!="":
       print output
   else:
       print "There was no output for this command"
   print("====================================================") """
##################### Test Case 5 #############################################
"""def verify_backup_back_end_dp():
   key_name=raw_input("Encryption key Name : ")
   os.environ['key_name'] = key_name
   secret=raw_input("Secret Name : ")
   os.environ['secret'] = secret
   payload=raw_input("Payload Name : ")
   os.environ['payload'] = payload
   os.system("source ~/overcloud && openstack secret order create --name $key_name --algorithm aes --mode ctr --bit-length 256 --payload-content-type=application")
   os.system("source ~/overcloud && openstack secret store --name $secret --payload $payload")
########################Test Case 8 ###########################
def verify_cinder():
   os.system("source ~/overcloud && crudini --get /var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf key_manager backend castellan.key_manager.barbican_key_manager.BarbicanKeyManager")
########################Test Case 9 ###########################
def verify_nova():
   os.system("source ~/overcloud && crudini --get /etc/nova/nova.conf key_manager backend castellan.key_manager.barbican_key_manager.BarbicanKeyManager")
"""
#######################
      
"""command_function(com)
com="cd /home/osp_admin;pwd"
command_function(com)
com="pwd"
command_function(com)
"""
################################### Functions Call ################################
launch_instance()

