#!/usr/bin/python

import os
import sys
from openstack import connection
import json

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
global_setup_file = "setup.json"

if os.path.exists(global_setup_file):
    data = None
    try:
        with open(global_setup_file) as data_file:
            data = json.load(data_file)
        data = {str(i): str(j) for i, j in data.items()}
    except:
        print ("\nFAILURE!!! error in %s file!"%global_setup_file)
else:
    print ("\nFAILURE!!! setup.json file not found!!!\nUnable to execute script\n\n")
    exit()

if os.path.exists(data["overcloud_rc_file_path"]):
    with open(data["overcloud_rc_file_path"]) as data_file:
        rc_file_cred = data_file.read()
    for line in rc_file_cred.split("\n"):
        if "OS_AUTH_URL" in str(line):
            os_auth_url = str(line.split("=")[1].strip())
        elif "OS_PASSWORD" in str(line):
            os_pass = str(line.split("=")[1].strip())
        elif "OS_PROJECT_NAME" in str(line):
            os_project_name = str(line.split("=")[1].strip())
        elif "OS_USERNAME" in str(line):
            os_username = str(line.split("=")[1].strip())
        elif "OS_PROJECT_DOMAIN_NAME" in str(line):
            os_domain_name = str(line.split("=")[1].strip())
else:
    print ("\nFAILURE!!! %s file not found!!!\nUnable to execute delete_os script\n\n" %data["overcloud_rc_file_path"] )
    exit()

class Os_Deletion_Modules():

    ### Creating Connection ###
    def os_connection_creation(self):
        conn = connection.Connection(auth_url=os_auth_url,
                                 #project_id="e46ed922a5a94fea968bc34bdb8f409d ",
                                 project_name=os_project_name,
                                 username=os_username,
                                 password=os_pass,
                                 #compute_api_version='1.1',
                                 domain_name=os_domain_name
                                 )
        return conn

    ### Deleting Flavor with Name###
    def os_deleting_flavor(self, logger, conn, name):
        logger.info("Deleting Flavor..")
        flavor = conn.delete_flavor(
            name_or_id=name
                                )
        if flavor:
            logger.info("Flavor Deleted successfully")
        else:
            logger.info("Deletion Failed")

    ### Deleting Keypair with Name###
    def os_deleting_keypair(self, logger, conn, name):
        logger.info("Deleting KeyPair..")
        keypair = conn.delete_keypair(
            name=name
        )
        if keypair:
            logger.info("KeyPair Deleted successfully")
        else:
            logger.info("Deletion Failed")

    ### Deleting Security group with Name and rules ###
    def os_deleting_security_group_and_rule(self, logger, conn, name):
        logger.info("Deleting Security Group and Adding Rules..")
        """sec_group = conn.create_security_group(
            name=name)"""
        sec_group = conn.get_security_group(name_or_id=name)

        for del_rule in sec_group.security_group_rules:
            ru = conn.delete_security_group_rule(del_rule.id)
            if ru:
                logger.info("Rule Deleted successfully")
            else:
                logger.info("Rule Deletion failed")

        global del_sec
        del_sec = conn.delete_security_group(name_or_id=name)
        if del_sec:
            logger.info("Group Deleted successfully")
        else:
            logger.info("Group Deletion failed")
        return del_sec

    ### Deleting Image with Name###
    def os_deleting_image(self, logger, conn, name):
        global image
        logger.info("Deleting Image..")
        image = conn.delete_image(
            name_or_id=name
        )
        if image:
            logger.info("Image Deleted successfully")
        else:
            logger.info("Image Deletion failed")
        return image


    ### Deleting Network without Router ###
    def os_delete_network_without_router(self, logger, conn, network_name):
        logger.info ("Deleting Network: %s.." % network_name)
        del_network = conn.delete_network(name_or_id=network_name)
        if del_network:
            logger.info ("Network deleted.")
        else:
            logger.info ("Unable to delete network!")
        return del_network


    ### Deleting Network with Router ###
    def os_deleting_router_with_1_network(self, logger, conn, network_name, router_name, port_name):
        global del_network
        global n_id
        global del_subnetwork
        global del_port
        global del_router
        global del_inter
        global subnet_id
        global router
        logger.info("Deleting Network & Router..")
        router=conn.get_router(name_or_id=router_name, filters=None)
        subnet_id_list = conn.get_network(
            name_or_id=network_name
        ).subnets
        #d_router=conn.get_router(name_or_id=network_name)
        #logger.info (d_router)
        logger.info("Deleting Interfaces..")
        for subnet_id in subnet_id_list:
            del_inter=conn.remove_router_interface(router, subnet_id=subnet_id, port_id=None)
            if del_inter:
                logger.info("Interface Deletion failed")
            else:
                logger.info("Interface Deleted successfully")
        logger.info("Deleting Port..")
        del_port=conn.delete_port(name_or_id=port_name)
        if del_port:
            logger.info("Port Deleted successfully")
        else:
            logger.info("Port Deletion failed")
        logger.info("Deleting Subnetwork..")
        for subnet_id in subnet_id_list:
            del_subnetwork=conn.delete_subnet(name_or_id=subnet_id)
            if del_subnetwork:
                logger.info("Subnet Deleted successfully")
            else:
                logger.info("Subnet Deletion failed")
        logger.info("Deleting Network..")
        del_network=conn.delete_network(name_or_id=network_name)
        if del_network:
            logger.info("Network Deleted successfully")
        else:
            logger.info("Network Deletion failed")
        logger.info("Deleting Router..")
        del_router = conn.delete_router(name_or_id=router_name)
        if del_router:
            logger.info("Router Deleted successfully")
        else:
            logger.info("Router Deletion failed")
        return del_router

    ####################sriov enabled network deletion for 2 instance on same network===================================
    ### Deleting Network with Router ###
    def os_deleting_router_with_1_network_sriov(self, logger, conn, network_name, router_name, port1_name, port2_name):
        global del_network
        global n_id
        global del_subnetwork
        global del_port
        global del_router
        global del_inter
        global subnet_id
        global router
        logger.info("Deleting Network & Router..")
        router=conn.get_router(name_or_id=router_name, filters=None)
        subnet_id_list = conn.get_network(
            name_or_id=network_name
        ).subnets
        #d_router=conn.get_router(name_or_id=network_name)
        p1_id=str(conn.get_port(name_or_id=port1_name).id)
        p2_id = str(conn.get_port(name_or_id=port2_name).id)
        #logger.info (d_router)
        logger.info("Deleting Interfaces..")
        for subnet_id in subnet_id_list:
            del_inter=conn.remove_router_interface(router, subnet_id=subnet_id, port_id=None)
            if del_inter:
                logger.info("Interface Deletion failed")
            else:
                logger.info("Interface Deleted successfully")
        logger.info("Deleting Port..")
        del_port=conn.delete_port(name_or_id=port1_name)
        if del_port:
            logger.info("Port Deleted successfully")
        else:
            logger.info("Port Deletion failed")
            del_inter = conn.remove_router_interface(router, subnet_id=subnet_id, port_id=None)
            if del_inter:
                logger.info("Interface Deletion failed")
            else:
                logger.info("Interface Deleted successfully")
        logger.info("Deleting Port..")
        del_port = conn.delete_port(name_or_id=port2_name)
        if del_port:
            logger.info("Port Deleted successfully")
        else:
            logger.info("Port Deletion failed")
        logger.info("Deleting Subnetwork..")
        for subnet_id in subnet_id_list:
            del_subnetwork=conn.delete_subnet(name_or_id=subnet_id)
            if del_subnetwork:
                logger.info("Subnet Deleted successfully")
            else:
                logger.info("Subnet Deletion failed")
        logger.info("Deleting Network..")
        del_network=conn.delete_network(name_or_id=network_name)
        if del_network:
            logger.info("Network Deleted successfully")
        else:
            logger.info("Network Deletion failed")
        logger.info("Deleting Router..")
        del_router = conn.delete_router(name_or_id=router_name)
        if del_router:
            logger.info("Router Deleted successfully")
        else:
            logger.info("Router Deletion failed")
        return del_router

    ### Deleting 2 Networks with Router ###
    def os_deleting_router_with_2_networks(self, logger, conn, network1_name, network2_name, router_name, port1_name, port2_name):
        global del_network
        global n_id
        global del_subnetwork
        global del_port
        global del_router
        global del_inter
        global subnet_id
        global router
        logger.info("Deleting Network: %s and %s" %(network1_name, network2_name))
        router=conn.get_router(name_or_id=router_name, filters=None)
        subnet1_id_list = conn.get_network(
            name_or_id=network1_name
        ).subnets
        subnet2_id_list = conn.get_network(
            name_or_id=network2_name
        ).subnets
        #d_router=conn.get_router(name_or_id=network_name)
        #logger.info (d_router)
        logger.info("Deleting Interfaces..")
        for subnet_id in subnet1_id_list:
            del_inter = conn.remove_router_interface(router, subnet_id=subnet_id, port_id=None)
            if del_inter:
                logger.info("Interface Deletion failed")
            else:
                logger.info("Interface Deleted successfully")
        logger.info("Deleting Interfaces..")
        for subnet_id in subnet2_id_list:
            del_inter = conn.remove_router_interface(router, subnet_id=subnet_id, port_id=None)
            if del_inter:
                logger.info("Interface Deletion failed")
            else:
                logger.info("Interface Deleted successfully")
        logger.info("Deleting Port..")
        del_port = conn.delete_port(name_or_id=port1_name)
        if del_port:
            logger.info("Port Deleted successfully")
        else:
            logger.info("Port Deletion failed")
        logger.info("Deleting Port..")
        del_port = conn.delete_port(name_or_id=port2_name)
        if del_port:
            logger.info("Port Deleted successfully")
        else:
            logger.info("Port Deletion failed")
        logger.info("Deleting Subnetwork..")
        for subnet_id in subnet1_id_list:
            del_subnetwork = conn.delete_subnet(name_or_id=subnet_id)
            if del_subnetwork:
                logger.info("Subnetwork Deleted successfully")
            else:
                logger.info("Subnetwork Deletion failed")
        logger.info("Deleting Subnetwork..")
        for subnet_id in subnet2_id_list:
            del_subnetwork = conn.delete_subnet(name_or_id=subnet_id)
            if del_subnetwork:
                logger.info("Subnetwork Deleted successfully")
            else:
                logger.info("Subnetwork Deletion failed")
        logger.info("Deleting Network..")
        del_network = conn.delete_network(name_or_id=network1_name)
        if del_network:
            logger.info("Network Deleted successfully")
        else:
            logger.info("Network Deletion failed")
        logger.info("Deleting Network..")
        del_network = conn.delete_network(name_or_id=network2_name)
        if del_network:
            logger.info("Network Deleted successfully")
        else:
            logger.info("Network Deletion failed")
        logger.info("Deleting Router: %s.." % router_name)
        del_router = conn.delete_router(name_or_id=router_name)
        if del_router:
            logger.info("Router Deleted successfully")
        else:
            logger.info("Router Deletion failed")
        return del_router

    ### Deleting Server with name ###
    def os_delete_server(self, logger, conn, server_name, min_count=1, max_count=1):
        global server
        count = 1
        if max_count > 1 or min_count > 1:
            while count <= max_count:
                instance_name = "%s-%s" %(server_name,count)
                logger.info ("Deleting Server: %s.." % instance_name)
                server = conn.delete_server(name_or_id= instance_name, wait=False, timeout=180, delete_ips=True, delete_ip_retry=1)
                if server:
                    logger.info ("Server Deleted successfully")
                else:
                    logger.info ("Server deletion failed!")
                count = count + 1
        else:
            instance_name = "%s" % server_name
            logger.info("Deleting Server: %s.." % instance_name)
            server = conn.delete_server(name_or_id=instance_name, wait=False, timeout=180, delete_ips=True,
                                        delete_ip_retry=1)
            if server:
                logger.info("Server Deleted successfully")
            else:
                logger.info("Server deletion failed!")

        f_ip_list = self.os_delete_detached_floating_ips(logger, conn)
        return f_ip_list


    def os_delete_vlanaware_server(self, logger, conn, server_name, parentport_name, subport_name, trunk_name,
                                   delete_parentport=True, delete_subport=True, delete_trunk=True, network_name=None):
        # ser = self.os_delete_server(logger, conn, server_name)

        if delete_trunk:
            logger.info("Deleting Trunk: %s.." % trunk_name)
            trunk_id = conn.network.get_trunk(trunk_name).id
            tr = conn.network.delete_trunk(trunk_id)
            if tr:
                logger.info ("Trunk Deleted successfully")
            else:
                logger.info ("Trunk deletion failed!")

        if delete_parentport:
            logger.info ("Deleting Parent Port: %s.." % parentport_name)
            pp = conn.delete_port(name_or_id=parentport_name)
            if pp:
                logger.info ("Parent Port Deleted successfully")
            else:
                logger.info ("Parent Port deletion failed!")

        if delete_subport:
            logger.info("Deleting Sub Port: %s.." % subport_name)
            sp = conn.delete_port(name_or_id=subport_name)
            if sp:
                logger.info ("Sub Port Deleted successfully")
            else:
                logger.info ("Sub Port deletion failed!")

        return [ser, pp, sp, tr]

    #### Deleting all detached Floating IPs ###
    def os_delete_detached_floating_ips(self, logger, conn):
        global dettached_floating_ips
        logger.info ("Deleting all unattached floating IPs.")
        dettached_floating_ips = conn.delete_unattached_floating_ips(retry=1)
        return dettached_floating_ips

    #### Deleting Zone ###
    def os_delete_zone(self, logger, conn, name):
        logger.info("Deleting zone %s"%name)
        zone = conn.delete_zone(name_or_id=name)
        return zone


############################################################################################################################################
########                        deleting 1 instance with 1 networks and 1 Router                                                    ########
############################################################################################################################################
    def delete_1_instance_and_router_with_1_network(self, logger, conn, server_name, network_name,
                                                     router_name, port_name):
        self.os_delete_server(logger, conn, server_name)
        self.os_deleting_router_with_1_network(logger, conn, network_name, router_name, port_name)


############################################################################################################################################
########                        deleting 2 instance with diff networks                                                              ########
############################################################################################################################################

    def delete_2_instances_and_router_with_2_networks(self, logger, conn, server1_name, server2_name, network1_name, network2_name,
                                                      router_name, port1_name, port2_name):
        self.os_delete_server(logger, conn, server1_name)
        self.os_delete_server(logger, conn, server2_name)
        self.os_deleting_router_with_2_networks(logger, conn, network1_name, network2_name, router_name, port1_name, port2_name)


############################################################################################################################################
########                        deleting 2 instance with same networks                                                              ########
############################################################################################################################################
    def delete_2_instances_and_router_with_1_network(self, logger, conn, server1_name, server2_name, network_name, router_name, port_name):
        self.os_delete_server(logger, conn, server1_name)
        self.os_delete_server(logger, conn, server2_name)
        self.os_deleting_router_with_1_network(logger, conn, network_name, router_name, port_name)


############################################################################################################################################
########                        deleting 2 instance with same networks with sriov enabled instances                                                            ########
###########################################################################
    def delete_2_instances_sriov_enabled_and_router_with_1_network(self, logger, conn, server1_name, server2_name,
                                                                   network_name, router_name, port1_name, port2_name):
        self.os_delete_server(logger, conn, server1_name)
        self.os_delete_server(logger, conn, server2_name)
        self.os_deleting_router_with_1_network_sriov(logger, conn, network_name, router_name, port1_name, port2_name)
    def delete_2_instances_and_router_with_1_network_2ports(self, logger, conn, server1_name, server2_name, network_name,
                                                            router_name, port1_name, port2_name):
        self.os_delete_server(logger, conn, server1_name)
        self.os_delete_server(logger, conn, server2_name)
        self.os_deleting_router_with_1_network(logger, conn, network_name, router_name, port_name=port1_name)
        # self.os_deleting_router_with_1_network(logger, conn, network_name, router_name, port_name=port2_name)

    def delete_2_instances_and_router_with_2_network_2ports(self, logger, conn, server1_name, server2_name,
                                                            network1_name, network2_name,
                                                            router_name, port1_name, port2_name):
        self.os_delete_server(logger, conn, server1_name)
        self.os_delete_server(logger, conn, server2_name)
        self.os_deleting_router_with_1_network(logger, conn, network_name=network1_name, router_name=router_name, port_name=port1_name)
        self.os_deleting_router_with_1_network(logger, conn, network_name=network2_name, router_name=router_name, port_name=port2_name)
# obj = Os_Deletion_Modules()
# conn=obj.os_connection_creation()
# obj.delete_1_instance_and_router_with_1_network(conn, server_name="test_vm", network_name="test_net",
#                                                      router_name="test_router", port_name="test_port")
# obj.os_delete_server(conn, "test-vm")
#obj.os_delete_server(conn, "test-")
# obj.os_deleting_network_and_router(conn, "test-vm", "test-vm", "sub-test-vm","test-vm")
#
# obj.os_deleting_security_group_and_rule(conn,"test-vm")
# obj.os_deleting_flavor(conn,"test-vm")
# obj.os_deleting_image(conn,"test-vm")
# obj.os_deleting_keypair(conn, "test-vm")


