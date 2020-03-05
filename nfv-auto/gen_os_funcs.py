#!/usr/bin/python

import os
import sys
from openstack import connection
import pdb

"""
	MODULES:
	1.Create Flavor
	2.Create KeyPair
	3.Create Security Group & Rules
	4.Create Image
	5.Create Private Network and subnetwork
	6.Create Router and Connect it to External Network
	7.Create 2 VMs from above Specs
	8.Floating IP assignment and creation
	9.SSH and ping those 2 VMs Created Above
"""

class Os_Modules():
    global conn
    global net_id
    global fla_id
    global img_id
    global sec_id

    def create_connection(self):
        global conn
        global pub_id
        conn = connection.Connection(auth_url="http://192.168.24.16:5000//v3", project_name="admin",
                                   username="admin", password="7Ekhk2rWaaXxukVc6eBWzcbAy",
                                     domain_name="Default")
        # pub_id = conn.get_network("public", filters=None).id
        return conn


    def os_create_flavor(self, conn, name, ram, vcpus, disk):
        global flavor
        print "Creating Flavor."
        flavor = conn.create_flavor(
                        name=name,
                        ram=ram,
                        vcpus=vcpus,
                        disk=disk)
        return flavor

    def os_create_keypair(self, conn, name, public_key=None):
        global keypair
        print "Creating KeyPair."
        keypair = conn.create_keypair(
            name=name)
        return keypair

    def os_create_security_group_and_rule(self, conn, name, desc, proto1, proto2, remote_ip, project_id=None):
        global sec_group
        print "Creating Security Group and Adding Rules."
        sec_group = conn.create_security_group(
            name=name,
            description=desc)
        rule = conn.create_security_group_rule(
            secgroup_name_or_id=name,
            protocol=proto1,
            remote_ip_prefix=remote_ip)
        rule = conn.create_security_group_rule(
            secgroup_name_or_id=name,
            protocol=proto2,
            remote_ip_prefix=remote_ip)
        return sec_group

    def os_create_image(self, conn, img_name, imag_file, dis_f, cont_f):
        global image
        print "Creating Image."
        image = conn.create_image(
            name=img_name,
            filename=imag_file,
            disk_format=dis_f,
            container_format=cont_f)
        return image
	
    def os_create_network(self, conn, net_name, cidr, subnet_name, gatewy):
        global network
        global n_id
        global subnetwork
        print "Creating Network."
        network = conn.network.create_network(
            name=net_name)
        n_id = network.id
        subnetwork = conn.network.create_subnet(
            network_id=n_id,
            cidr=cidr,
            name=subnet_name,
            ip_version="4",
            gateway_ip=gatewy)
        return network

    def os_create_router(self, conn, router_name, port_name, net_name):
        global port_id
        global router
        global net_id
        global subnet_id
        global pub_id
        print "Creating Router."
        pub_id = conn.get_network("provider",filters=None).id

        router = conn.create_router(
            name=router_name,
            ext_gateway_net_id=pub_id)

        net_id = conn.get_network(
            net_name,
            filters=None).id

        port_id = conn.create_port(
            network_id=net_id,
            name=port_name)

        subnet_id = conn.get_network(
            name_or_id=net_name).subnets[0]

        router_to_subnet = conn.add_router_interface(
            router=router,
            subnet_id=subnet_id)

        return router

    def os_create_aggregate_and_add_host(self, conn, name, availablity_zone, host_name):
        global aggregate
        print "Creating aggregate and adding host."
        aggregate = conn.create_aggregate(name, availability_zone=availablity_zone)
        conn.add_host_to_aggregate(name, host_name)
        return aggregate

    def os_create_server(self, conn, server_name, flavor_name, image_name, network_name, secgroup_name):
        global server
        global f_id
        global i_id
        global n_id
        global s_id
        print "Creating Server."

        f_id = conn.get_flavor(
            name_or_id=flavor_name,
            filters=None,
            get_extra=False).id

        i_id = conn.get_image(
            image_name,
            filters=None).id

        n_id = conn.get_network(
            network_name,
            filters=None).id

        s_id = conn.get_security_group(
            secgroup_name,
            filters=None).id

        server = conn.create_server(
            name=server_name,
            image=i_id,
            flavor=f_id,
            network=n_id,
            security_groups=s_id)
        return server

    def os_create_and_assign_floating_ip(self, conn, server_name):
        global floating
        global pub_id
        print "Creating and Assigning Floating IP."
        ser_obj = conn.get_server(name_or_id=server_name)
        floating = conn.create_floating_ip(
              network=pub_id,
              server=ser_obj)
              #fixed_address=ser_obj.private_v4)
        return floating



obj = Os_Modules()
conn = obj.create_connection()
obj.os_create_flavor(conn, "F1", 1024, 1, 20)
obj.os_create_keypair(conn, "F1")
obj.os_create_security_group_and_rule(conn, "F1", "F1", "tcp", "icmp", "0.0.0.0/0")
obj.os_create_image(conn, "F1", "/home/stack/cirros-0.4.0-i386-disk.img", "qcow2","bare")
obj.os_create_network(conn, "F1", "192.168.20.0/24", "sub-F1", "192.168.20.1")
obj.os_create_router(conn, "F1", "F1", "F1")
obj.os_create_aggregate_and_add_host(conn, "F1", "nova", "local-compute-0.localdomain")
obj.os_create_server(conn, "F1", "F1", "F1", "F1", "F1")
obj.os_create_and_assign_floating_ip(conn, "F1")

