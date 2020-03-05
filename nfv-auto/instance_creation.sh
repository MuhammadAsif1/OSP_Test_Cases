#!/bin/bash
#for i in {1..10}; do openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova0  ceph-nova0-vm-$i && echo "Server ceph-nova0-vm-$i created successfully"; done
#for i in {1..10}; do openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova1  ceph-nova1-vm-$i && echo "Server ceph-nova1-vm-$i created successfully"; done
#for i in {1..10}; do openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova2  ceph-nova2-vm-$i && echo "Server ceph-nova2-vm-$i created successfully"; done

#for i in {1..4}; do openstack server create --image ceph_med_vm_snap --flavor ceph-2vol --network storage-net --security-group c11a0ebb-22bb-4658-9804-c20d0053412a --key-name ceph-key --availability-zone nova1  ceph-net1-nova1-vm-$i && echo "Volume attached to server ceph-net1-nova1-vm-$i successfully"; done

#for i in {1..4}; do openstack server create --image ceph_med_vm_snap --flavor ceph-2vol --network storage-net --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name ceph-key --availability-zone nova2  ceph-net1-nova2-vm-$i && echo "Volume attached to server ceph-net1-nova2-vm-$i successfully"; done

#for i in {1..6}; do openstack server create --image ceph_med_vm_snap --flavor ceph-2vol --network storage-net2 --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name ceph-key --availability-zone nova0  ceph-net2-nova0-vm-$i && echo "server created ceph-net2-nova0-vm-$i successfully"; done

#for i in {1..6}; do openstack server create --image ceph_med_vm_snap --flavor ceph-2vol --network storage-net2 --security-group c11a0ebb-22bb-4658-9804-c20d0053412a --key-name ceph-key --availability-zone nova1  ceph-net2-nova1-vm-$i && echo "server ceph-net2-nova1-vm-$i created successfully"; done

#for i in {1..6}; do openstack server create --image ceph_med_vm_snap --flavor ceph-2vol --network storage-net2 --security-group c11a0ebb-22bb-4658-9804-c20d0053412a --key-name ceph-key --availability-zone nova2  ceph-net2-nova2-vm-$i && echo "server ceph-net2-nova2-vm-$i created successfully"; done

#########=========================================================================================######################
#for i in {53..60}; do openstack volume create --size 124 --bootable $i && echo "Volume created $i"; done

#for i in {1..10}; do openstack server add volume ceph-nova0-vm-$i $i && echo "Volume attached to server ceph-nova0-vm-$i  $i"; done

#for i in {1..10}; do openstack server add volume ceph-nova1-vm-$i $((i+10)) && echo "Volume attached to server ceph-nova1-vm-$i  $((i+10))"; done

#for i in {1..10}; do openstack server add volume ceph-nova2-vm-$i $((i+20)) && echo "Volume attached to server ceph-nova2-vm-$i  $((i+20))"; done

#for i in {1..10}; do openstack server add volume ceph-nova0-vm-$i $((i+30)) && echo "Volume attached to server ceph-nova0-vm-$i  $((i+30))"; done

#for i in {1..10}; do openstack server add volume ceph-nova1-vm-$i $((i+40)) && echo "Volume attached to server ceph-nova1-vm-$i  $((i+40))"; done

#for i in {1..10}; do openstack server add volume ceph-nova2-vm-$i $((i+50)) && echo "Volume attached to server ceph-nova2-vm-$i  $((i+50))"; done
#########=========================================================================================######################
#for i in {1..6}; do openstack server add volume ceph-net2-nova0-vm-$i $((i+42)) && echo "Volume attached to server ceph-net1-nova2-vm-$i"; done

#for i in {1..6}; do openstack server add volume ceph-net2-nova1-vm-$i $((i+48)) && echo "Volume attached to server ceph-net1-nova2-vm-$i"; done

#for i in {1..6}; do openstack server add volume ceph-net2-nova2-vm-$i $((i+54)) && echo "Volume attached to server ceph-net1-nova2-vm-$i"; done

#openstack floating ip list

#net1_floating_ip=(100.82.36.226 100.82.36.239 100.82.36.213 100.82.36.205 100.82.36.232 100.82.36.210 100.82.36.206 100.82.36.219 100.82.36.228 100.82.36.216 100.82.36.223 100.82.36.215)

#net2_floating_ip=(100.82.36.167 100.82.36.180 100.82.36.178 100.82.36.172 100.82.36.173 100.82.36.171 100.82.36.182 100.82.36.175 100.82.36.169 100.82.36.177 100.82.36.179 100.82.36.181 100.82.36.174 100.82.36.176 100.82.36.170 100.82.36.185 100.82.36.184 100.82.36.183)

#net1_vm_list=(ceph-net1-nova0-vm-1 ceph-net1-nova0-vm-2 ceph-net1-nova0-vm-3 ceph-net1-nova0-vm-4 ceph-net1-nova1-vm-1 ceph-net1-nova1-vm-2 ceph-net1-nova1-vm-3 ceph-net1-nova1-vm-4 ceph-net1-nova2-vm-1 ceph-net1-nova2-vm-2 ceph-net1-nova2-vm-3 ceph-net1-nova2-vm-4)

#net2_vm_list=(ceph-net2-nova0-vm-1 ceph-net2-nova0-vm-2 ceph-net2-nova0-vm-3 ceph-net2-nova0-vm-4 ceph-net2-nova0-vm-5 ceph-net2-nova0-vm-6 ceph-net2-nova1-vm-1 ceph-net2-nova1-vm-2 ceph-net2-nova1-vm-3 ceph-net2-nova1-vm-4 ceph-net2-nova1-vm-5 ceph-net2-nova1-vm-6 ceph-net2-nova2-vm-1 ceph-net2-nova2-vm-2 ceph-net2-nova2-vm-3 ceph-net2-nova2-vm-4 ceph-net2-nova2-vm-5 ceph-net2-nova2-vm-6)


#for i in "${net1_floating_ip[@]}"; do echo "$i" && openstack server add floating ip ; done
#for i in {0..12}; do openstack server add floating ip "${net1_vm_list[$((i))]}" "${net1_floating_ip[$((i))]}" && echo "openstack server add floating ip "${net1_floating_ip[$((i))]}" "${net1_vm_list[$((i))]}""; done

#for i in {1..10};do openstack port list --server "ceph-nova0-vm-$i" | awk -F "|" '/-/ {print $2}' | xargs -I{} openstack floating ip create --port {} public; echo "attached and created ceph-nova0-vm-$i"; done
#for i in {1..10};do openstack port list --server "ceph-nova1-vm-$i" | awk -F "|" '/-/ {print $2}' | xargs -I{} openstack floating ip create --port {} public; echo "attached and created ceph-nova0-vm-$i"; done
#for i in {7..10};do openstack port list --server "ceph-nova2-vm-$i" | awk -F "|" '/-/ {print $2}' | xargs -I{} openstack floating ip create --port {} public; echo "attached and created ceph-nova0-vm-$i"; done
#########=========================================================================================######################
#for i in {1..30}; do openstack server add floating ip "${net2_vm_list[$((i))]}" "${net2_floating_ip[$((i))]}" && echo "openstack server add floating ip "${net1_floating_ip[$((i))]}" "${net1_vm_list[$((i))]}""; done
#########=========================================================================================######################


openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova0  ceph-nova0-vm-3
openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova0  ceph-nova0-vm-7
openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova0  ceph-nova0-vm-10
openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova1  ceph-nova1-vm-3
openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova1  ceph-nova1-vm-5
openstack server create --image fio_image --flavor fio_flavor --network octavia-network --security-group 6be632f6-5ec6-4512-8a10-9fc550363f78 --key-name barbican_keypair --availability-zone nova2  ceph-nova2-vm-4