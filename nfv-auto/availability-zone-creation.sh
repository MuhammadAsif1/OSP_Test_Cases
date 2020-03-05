#!/bin/bash

compute_0_host=$(openstack host list | grep compute-0 | awk '/|/ {print $2}')
compute_1_host=$(openstack host list | grep compute-1 | awk '/|/ {print $2}')
compute_2_host=$(openstack host list | grep compute-2 | awk '/|/ {print $2}')
openstack aggregate create --zone nova0 nova0
openstack aggregate create --zone nova1 nova1
openstack aggregate create --zone nova2 nova2
openstack aggregate add host nova0 $compute_0_host
openstack aggregate add host nova1 $compute_1_host
openstack aggregate add host nova2 $compute_2_host
