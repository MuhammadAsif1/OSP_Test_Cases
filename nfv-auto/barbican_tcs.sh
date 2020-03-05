#!/bin/bash

################## ------- Varibales ----------###################
###-- 3 compute nodes ---##
compute_node1_ip='192.168.120.42'
compute_node2_ip='192.168.120.30'
compute_node3_ip='192.168.120.25'
###-- 3 controller nodes ---##
controller_node1_ip='192.168.120.47'
controller_node2_ip='192.168.120.38'
controller_node3_ip='192.168.120.34'
barbican_parameter='command' # value of this parameter ----> castellan.key_manager.barbican_key_manager.BarbicanKeyManager
#verify glance is configured to use barbican
glance_parameter='True'

volume_template='LuksEncryptor-Template-256'
encrypted_volume='Encrypted-Test-Volume'
unencrypted_volume='volume-1'
private_key='private_key.pem'
public_key='public_key.pem'
cert_request='cert_request.csr'
signed_cert='x509_signing_cert.crt'
singned_cert_key='signing-cert'
cloud_file='/home/osp_admin/CentOS-7-x86_64-GenericCloud.qcow2'
signing_image='centos-7.signature'
signing_image_b64='centos-7.signature.b64'
image='centos_7_signed'
network='network1'
subnet='subnet1'
router='router1'
public_network='public'
flavor='flavor1'
security_group='----------'
instance='barbican_instance'

href_value=''
href_id=''

############################################## ---- Functions ---------#####################################################

mkdir /home/osp_admin/barbican_keys

verify_glance_with_barbican()
{
  output1=$(ssh heat-admin@$compute_node1_ip 'cat /var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-api.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager') # this should be executed for that ----> cat /var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-api.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager
  	
  output2=$(ssh heat-admin@$compute_node2_ip 'cat /var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-api.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')
  
  output3=$(ssh heat-admin@$compute_node3_ip 'cat /var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-api.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')

  output4=$(ssh heat-admin@$compute_node1_ip 'crudini --get /var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf verify_glance_signatures')

  output5=$(ssh heat-admin@$compute_node2_ip 'crudini --get /var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf verify_glance_signatures')

  output6=$(ssh heat-admin@$compute_node3_ip 'crudini --get /var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf verify_glance_signatures')

  if [ $barbican_parameter = $output1 ] && [ $barbican_parameter = $output2 ] && [ $barbican_parameter = $output3 ] && [ $glance_parameter = $output4 ] && [ $glance_parameter = $output5 ] && [ $glance_parameter = $output6 ]
  then
    echo $output
    echo '========================================================================================='
    echo '========== Test Case executed Successfully, Glance is enabled to use Barbican ==========='
    echo '========================================================================================='
  else
    echo '========================================================================================='
    echo '=============== Test Case Failed, Glance is not enabled to use Barbican ================='
    echo '========================================================================================='
  fi   
}
#########################################################################
verify_cinder_uses_barbican()
{
  output1=$(ssh heat-admin@$controller_node1_ip 'cat /var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager') # this should be executed for that ----> 'cat /var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager
  
  output2=$(ssh heat-admin@$controller_node2_ip 'cat /var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')
  
  output3=$(ssh heat-admin@$controller_node1_ip 'cat /var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')
  
  if [ $barbican_parameter = $output1 ] && [ $barbican_parameter = $output2 ] && [ $barbican_parameter = $output3 ]
  then
    echo $output
    echo '========================================================================================='
    echo '========== Test Case executed Successfully, Cinder is enabled to use Barbican ==========='
    echo '========================================================================================='
  else
    echo '========================================================================================='
    echo '=============== Test Case Failed, Cinder is not enabled to use Barbican ================='
    echo '========================================================================================='
  fi   
}
###########################################################################
verify_nova_uses_barbican()
{
  output1=$(ssh heat-admin@$compute_node1_ip 'cat /var/lib/config-data/nova-libvirt/etc/nova/nova.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager') # this should be executed for that ----> ' cat /var/lib/config-data/nova-libvirt/etc/nova/nova.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager
  output2=$(ssh heat-admin@$compute_node2_ip 'cat /var/lib/config-data/nova-libvirt/etc/nova/nova.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')
  output3=$(ssh heat-admin@$compute_node3_ip 'cat /var/lib/config-data/nova-libvirt/etc/nova/nova.conf | grep castellan.key_manager.barbican_key_manager.BarbicanKeyManager')
  if [ $barbican_parameter = $output1 ] && [ $barbican_parameter = $output2 ] && [ $barbican_parameter = $output3 ]
  then
    echo $output
    echo '========================================================================================='
    echo '========== Test Case executed Successfully, Cinder is enabled to use Barbican ==========='
    echo '========================================================================================='
  else
    echo '========================================================================================='
    echo '=============== Test Case Failed, Cinder is not enabled to use Barbican ================='
    echo '========================================================================================='
  fi   
}
############################################################################
encrypted_volume_creation()
{
  openstack volume type create --encryption-provider nova.volume.encryptors.luks.LuksEncryptor --encryption-cipher aes-xts-plain64 --encryption-key-size 256 --encryption-control-location front-end $volume_template
  openstack volume create --size 1 --type LuksEncryptor-Template-256 $encrypted_volume
  sleep 1m
  output=$(openstack volume show $encrypted_volume | grep available )
  if [ $output = '| status                         | available                             |']
  then
    echo '========================================================================================='
    echo '================= Test Case executed Successfully, Encrypted Volume is created ===================='
    echo '========================================================================================='
  else
    echo '========================================================================================='
    echo '======================= Test Case Failed, Encrypted volume not created ============================'
    echo '========================================================================================='
  fi
  volume_id=$(openstack volume show $encrypted_volume | grep -w id)
}
#################################################################################
verify_addition_of_key_to_barbican_secret_store()
{
  rm -rf /home/osp_admin/barbican_keys/*
  ##Generate a private key and convert it to the required format
  openssl genrsa -out /home/osp_admin/barbican_keys/$private_key 1024
  openssl rsa -pubout -in /home/osp_admin/barbican_keys/$private_key -out /home/osp_admin/barbican_keys/$public_key
  openssl req -new -key /home/osp_admin/barbican_keys/$private_key -out /home/osp_admin/barbican_keys/$cert_request
  openssl x509 -req -days 14 -in /home/osp_admin/barbican_keys/$cert_request -signkey /home/osp_admin/barbican_keys/$private_key -out /home/osp_admin/barbican_keys/$signed_cert
  ##Add the key to the barbican secret store
  href_value=$(openstack secret store --name $singned_cert_key --algorithm RSA --secret-type certificate --payload-content-type "application/octet-stream" --payload-content-encoding base64  --payload "$(base64 /home/osp_admin/barbican_keys/$signed_cert)" -c 'Secret href' -f value)  ###some doubts in this command
  ###
  href_id=$(echo $href_value | awk -F '/' '{print $6}')
  echo $href_id
  echo '==== if signed key shown than test case executed successfully otherwise failed ========='
  if [ $(openstack secret show $href_value | grep $singned_cert_key) != ' ' ]
  then
    echo "Barbican Secret Key added Successfully"
  else
    echo "Barbican Secret Key Failed to add"
    rm -rf /home/osp_Admin/barbican_keys/*
  fi
}
####################################################################################
creating_signed_image()
{
##call function inside it, if needed
  verify_addition_of_key_to_barbican_secret_store
  ##Use private_key.pem to sign the image and generate the .signature file
  openssl dgst -sha256 -sign /home/osp_admin/barbican_keys/$private_key -sigopt rsa_padding_mode:pss -out /home/osp_admin/barbican_keys/$signing_image /home/osp_admin/$cloud_file
  ##Convert the resulting .signature file into base64 format
  base64 -w 0 /home/osp_admin/barbican_keys/$signing_image > /home/osp_admin/barbican_keys/$signing_image_b64
  ###Load the base64 value into a variable to use it in the subsequent command
  image_signature_b64=$(cat /home/osp_admin/barbican_keys/$signing_image_b64)
  ##### Upload the signed image to glance. For img_signature_certificate_uuid, you must specify the UUID of the signing key you previously uploaded to barbican
  openstack image create --container-format bare --disk-format qcow2 --property img_signature='$image_signature_b64' --property img_signature_certificate_uuid=$href_id --property img_signature_hash_method='SHA-256' --property img_signature_key_type='RSA-PSS' $image < $cloud_file
  if [ $(openstack image show $image | awk '/status/ {print $4}') = 'active' ]
  then
    echo "Image Created Successfully"
  else
    echo "Image Creation Failed"
    rm -rf /home/osp_Admin/barbican_keys/*
  fi
}
###################################################################################

###################################################################################
creating_network_and_server()
{
  openstack network create $network
  openstack subnet create $subnet --network $network --subnet-range 192.168.50.0/24
  openstack router create $router
  openstack router set $router --external-gateway $public_network
  ###Adding Private Subnet to Router
  openstack router add subnet $router $subnet
  ### creating keypair
  openstack keypair create ssh-key >> /home/osp_admin/ssh-key.pem
  chmod 400 /home/osp_admin/ssh-key.pem
  ### creating server
  openstack server create --flavor $flavor --image $image --key-name ssh-key --security-group $security_group --network $network $instance
  sleep 1m
  output=$(openstack server show $instance | grep status )
  status=$(awk '{ if($4 == "active") print $4;}' awk.txt)
  if [ $status = 'active']
  then
    echo '========================================================================================='
    echo '===================== Instance created  Created successfully ============================'
    echo '========================================================================================='
    for i in {1};do openstack port list --server "$instance" | awk -F "|" '/-/ {print $2}' | xargs -I{} openstack floating ip create --port {} public; echo "$instance"; done
#    openstack floating ip create $public_network
#    #assign floating ip to instance
#    echo '=========== List of Floating IPs =============='
#    openstack floating ip list
#    echo 'Enter created floating ip = '
#    read Floating_IP
#    openstack server add floating ip $instance $Floating_IP
#    output=$(ping -c 1 $Floating_IP &> /dev/null && echo success || echo fail)
    Floating_IP=$(openstack server list | awk '{ if($4 == "$instance") print $10}')
    output=$(ping -c 1 $Floating_IP &> /dev/null && echo success || echo fail)
    if [ $output = 'success']
    then
      echo '=========================== instance is reachable from external network ==========='
      ping $Floating_IP
    else 
      echo '=========================== ping unsuccessfull, test case failde ==========='
      ping $Floating_IP
    fi
  else
    echo '========================================================================================='
    echo '======================= Test Case Failed, Encrypted Instance not created ============================'
    echo '========================================================================================='
  fi
}
###################################################################################
attach_encrypted_volume_to_existing_instance()
{
  #openstack server add volume $instance $encrypted_volume
  openstack volume create --size 5 --bootable $unencrypted_volume
  openstack server add volume $instance $unencrypted_volume
  if [ $(openstack server show $instance | awk '/volumes_attached/ {print $4}') = '|' ]
  then
    echo "volume Attaced failed / No volume Attached"
  else
    echo "Volume Attached Successfully"
  fi
}
#############---------- Main ------------#############

verify_glance_with_barbican
verify_cinder_uses_barbican
verify_nova_uses_barbican
#encrypted_volume_creation
#verify_addition_of_key_to_barbican_secret_store ## this should be called in 'creating_signed_image', if needed 
#creating_signed_image
#creating_network_and_server
#attach_encrypted_volume_to_existing_instance
