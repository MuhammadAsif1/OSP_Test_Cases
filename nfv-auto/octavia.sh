#!/bin/bash

NETWORK_NAME=octavia-net
SUBNET_NAME=octavia-subnet
SUBNET_RANGE=192.168.100.0/24
SUBNET_GATEWAY=192.168.100.1
ROUTER_NAME=octavia-router
EXTERNAL_NETWORK=public

SECURITY_GROUP_NAME=5ffacd02-d1a0-4682-abf3-b427f0c61831
FLAVOR_NAME=sanity_flavor
IMAGE_URL=http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2
IMAGE_FILE_NAME=CentOS-7-x86_64-GenericCloud.qcow2
IMAGE_NAME=centos
KEYPAIR_NAME=dvr-key

SERVER_1_NAME=octavia-vm1
SERVER_2_NAME=octavia-vm2

ZONE=nova1
#############Functions######
#########FUNCTION_1
execute_command(){
  cmd="$1"

  info "Executing: $cmd"

  $cmd
  if [ $? -ne 0 ]; then
    echo "command failed"
    exit 1
  fi
}
#########FUNCTION_2
create_the_networks(){
  info "### Creating the Network ####"
  net_exists=$(openstack network list -c Name -f value | grep "$NETWORK_NAME")
  if [ "$net_exists" != "$NETWORK_NAME" ]
  then
    execute_command "openstack network create $NETWORK_NAME "
  else
    info "#----- network '$NETWORK_NAME' exists. Skipping"
  fi
  info "### Creating the Sub Network ####"
  subnet_exists=$(openstack subnet list -c Name -f value | grep "$SUBNET_NAME")
  if [ "$subnet_exists" != "$SUBNET_NAME" ]
  then
    set_tenant_scope
    execute_command "openstack subnet create $SUBNET_NAME --network $NETWORK_NAME --subnet-range $SUBNET_RANGE --gateway $SUBNET_GATEWAY"
  else
    info "#----- '$NETWORK_NAME' Network subnet '$SUBNET_NAME' exists. Skipping"
  fi
  info "### Creating the Router ####"
  net_exists=$(openstack router list -c Name -f value | grep "$ROUTER_NAME")
  if [ "$net_exists" != "$ROUTER_NAME" ]
  then
    execute_command "openstack router create $ROUTER_NAME "
  else
    info "#----- router '$ROUTER_NAME' exists. Skipping"
  fi
  info "### Adding Networks into Router ####"
  execute_command "openstack router add subnet $ROUTER_NAME $SUBNET_NAME"
  execute_command "openstack router set $ROUTER_NAME --external-gateway $EXTERNAL_NETWORK"
}
#########FUNCTION_3
setup_image(){
  image_exists=$(openstack image list -c Name -f value | grep -x $IMAGE_NAME)
  if [ "$image_exists" != "$IMAGE_NAME" ]
  then
    if [ ! -f ./$IMAGE_FILE_NAME ]; then
      sleep 5 #HACK: a timing issue exists on some stamps -- 5 seconds seems sufficient to fix it
      info "### Downloading CentOS image file. Please wait..."
      wget --progress=bar:force $IMAGE_URL
      if [ $? -ne 0 ]; then
        echo "command failed"
        exit 1
      fi
      info "### Download complete."
    else
      info "#----- CentOS image exists. Skipping"
    fi
    execute_command "openstack image create --disk-format qcow2 --container-format bare --file $IMAGE_FILE_NAME $IMAGE_NAME"
  else
    info "#----- Image '$IMAGE_NAME' exists. Skipping"
  fi
  execute_command "openstack image list"
}
#########FUNCTION_4
instance_1_spinup(){
  info "### Creating Instance ####"
  net_exists=$(openstack server list -c Name -f value | grep "SERVER_1_NAME")
  if [ "$net_exists" != "SERVER_1_NAME" ]
  then
    execute_command "openstack server create --network $NETWORK_NAME --image $IMAGE_NAME --flavor $FLAVOR_NAME --security-group $SECURITY_GROUP_NAME --key-name $KEYPAIR_NAME --availability-zone $ZONE SERVER_1_NAME"
  else
    info "#----- Server 'SERVER_1_NAME' exists. Skipping"
  fi
}
#########FUNCTION_5
instance_2_spinup(){
  info "### Creating Instance ####"
  net_exists=$(openstack server list -c Name -f value | grep "SERVER_2_NAME")
  if [ "$net_exists" != "SERVER_2_NAME" ]
  then
    execute_command "openstack server create --network $NETWORK_NAME --image $IMAGE_NAME --flavor $FLAVOR_NAME --security-group $SECURITY_GROUP_NAME --key-name $KEYPAIR_NAME --availability-zone $ZONE SERVER_2_NAME"
  else
    info "#----- Server 'SERVER_1_NAME' exists. Skipping"
  fi
}

info "========================================================="
info "======================Octavia Script====================="
info "========================================================="
create_the_networks()

setup_image()

instance_1_spinup()

instance_2_spinup()