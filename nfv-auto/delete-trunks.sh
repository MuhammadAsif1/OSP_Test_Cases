#!/bin/bash
echo "Deleting trunk port"
openstack network trunk delete trunk_port
echo "Trunk port Deletion Successful"
echo "Deleting Parent port"
openstack port delete parent_port
echo "Parent port Deletion Successful"
echo "Deleting Sub Port"
openstack port delete sub_port
echo "Sub port Deletion Successful"

