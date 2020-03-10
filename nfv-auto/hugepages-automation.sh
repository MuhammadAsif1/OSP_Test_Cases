#!/bin/bash

################## ------- Varibales ----------###################
###-- 3 compute nodes ---##
compute_node1_ip='nova0'
compute_node2_ip='nova1'
compute_node3_ip='nova2'
###-- 3 controller nodes ---##
controller_node1_ip='cntrl0'
controller_node2_ip='cntrl1'
controller_node3_ip='cntrl2'

hugepagesize=1000000 ## value in kB, which is equal to 1 GB
flavor='hpg_flavor1'
network='hugpages_network1'
subnet='hugpages_subnet1'
router='hugpages_router1'
image='centos'
instance='vm1'
public_network='public'
security_group='1047ba76-637d-4ae2-b2ae-d3bb8ce66391'
availability_zone='nova0'
################################################
validate_deployment_with_hugepage_size_set_to_1gb()
{
  output1=$(ssh heat-admin@$compute_node1_ip 'grep "Huge" /proc/meminfo')
  echo "=================== Compute node 1 ==========================="
  echo "=================== Compute node 1 ===========================" > validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output1" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output1" 
  output2=$(ssh heat-admin@$compute_node2_ip 'grep "Huge" /proc/meminfo')
  echo "=================== Compute node 2 ==========================="
  echo "=================== Compute node 2 ===========================" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output2" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output2"
  output3=$(ssh heat-admin@$compute_node3_ip 'grep "Huge" /proc/meminfo')
  echo "=================== Compute node 3 ==========================="
  echo "=================== Compute node 3 ===========================" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output3" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  echo "$output3"
  output1=$(echo "$output1" | awk '/Hugepagesize/ {print $2}')
  output2=$(echo "$output2" | awk '/Hugepagesize/ {print $2}')
  output3=$(echo "$output3" | awk '/Hugepagesize/ {print $2}')
  if [ $output1 -lt $hugepagesize ] && [ $output2 -lt $hugepagesize ] && [ $output3 -lt $hugepagesize ]
  then
    echo "======================= Failed, Huge Page Size is not 1 GB =================="
    echo "======================= Failed, Huge Page Size is not 1 GB ==================" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  else
    echo "======================= Successfully executed, Huge Page Size is 1 GB =================="
    echo "======================= Successfully executed, Huge Page Size is 1 GB ==================" >> validate_deployment_with_hugepage_size_set_to_1gb.log
  fi
}
###############################################################################
network_setup()
{
   output1=$(openstack network create $network)
   echo "$output1" > network_setup.log
   echo "$output1" 
   output1=$(openstack subnet create $subnet --network $network --subnet-range 192.168.50.0/24)
   echo "$output1" >> network_setup.log
   echo "$output1"
   output1=$(openstack router create $router)
   echo "$output1" >> network_setup.log
   echo "$output1"
   output1=$(openstack router add subnet $router $subnet)
   echo "$output1" >> network_setup.log
   echo "$output1"
   output1=$(openstack router set $router --external-gateway $public_network)
   echo "$output1" >> network_setup.log
   echo "$output1"
}

###############################################################################
instance_creation_using_hugepage_flavor()
{
  ## flavor creation
  output1=$(openstack flavor create --id auto --ram 4096 --disk 40 --vcpu 2 $flavor)
  echo "$output1" > instance_creation_using_hugepage_flavor.log
  echo "$output1"
  #### setting properties of flavor
  output1=$(openstack flavor set --property "hw:mem_page_size"="1048576" --property "aggregate_instance_extra_specs:hugepages"="True" $flavor)
  echo "$output1" >> instance_creation_using_hugepage_flavor.log
  echo "$output1"
  ## creating keypair
  if [ $(ls /home/osp_admin/ | grep ssh-key.pem) = 'ssh-key.pem' ]
  then
    chmod 400 /home/osp_admin/ssh-key.pem
  else
    output1=$(openstack keypair create ssh-key > /home/osp_admin/ssh-key.pem)
    echo "$output1" >> instance_creation_using_hugepage_flavor.log
    echo "$output1"
    ### setting permission to .pem file
    output1=$(chmod 400 /home/osp_admin/ssh-key.pem)
    echo "$output1" >> instance_creation_using_hugepage_flavor.log
    echo "$output1"
  fi
  ## server creation 
  output1=$(openstack server create --flavor $flavor --image $image --key-name ssh-key --security-group $security_group --network $network --availability-zone $availability_zone $instance)
  echo "$output1" >> instance_creation_using_hugepage_flavor.log
  echo "$output1"
  sleep 2m 
  
  output=$(openstack server show $instance | awk '/status/ {print $4}')
  if [ $output = 'ACTIVE' ]
  then
    echo '========================================================================================='
    echo '===================== Instance created  Created successfully ============================'
    echo '========================================================================================='
    echo '===================== Instance created  Created successfully ============================' >> instance_creation_using_hugepage_flavor.log
    for i in {1};do openstack port list --server "$instance" | awk -F "|" '/-/ {print $2}' | xargs -I{} openstack floating ip create --port {} public; echo "$instance"; done
    
    echo "creating floating ip ........... " >> instance_creation_using_hugepage_flavor.log
    Floating_IP=$(openstack server list | awk "/$instance/"'{print $9}')
    echo "$Floating_IP" >> instance_creation_using_hugepage_flavor.log
    sleep 10
    output=$(ping -c 1 $Floating_IP &> /dev/null && echo success || echo fail)
    if [ $output = 'success' ]
    then
      echo '=========================== instance is reachable from external network ==========='
      echo '=========================== instance is reachable from external network ===========' >> instance_creation_using_hugepage_flavor.log
      ping -w $Floating_IP
    else 
      echo '=========================== ping unsuccessfull, test case failde ==========='
      echo '=========================== ping unsuccessfull, test case failde ===========' >> instance_creation_using_hugepage_flavor.log
      ping -w $Floating_IP
    fi
  else
    echo '========================================================================================='
    echo '========================== Failed, Instance not created ======================='
    echo '========================================================================================='
    echo '========================== Failed, Instance not created =======================' >> instance_creation_using_hugepage_flavor.log
  fi
  ###################
  output=$(ssh $availability_zone 'virsh dumpxml $instance')
  echo "$output"
  echo "$output" >> instance_creation_using_hugepage_flavor.log
  output=$(ssh $availability_zone 'grep "Huge /proc/meminfo"')
  echo "$output"
  echo "$output" >> instance_creation_using_hugepage_flavor.log
}
############################### ----------- Main ---------------- #######################
#validate_deployment_with_hugepage_size_set_to_1gb
#network_setup
instance_creation_using_hugepage_flavor
