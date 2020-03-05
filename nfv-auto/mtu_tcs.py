import commands
import os
import time
import json
import sys
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import iperf3_funcs
import pdb
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime


ssh_obj = ssh_functions()
creation_object = Os_Creation_Modules()
delete_object = Os_Deletion_Modules()
conn_create = creation_object.os_connection_creation()
conn_delete = delete_object.os_connection_creation()

mtu_test_cases_dict = {
    3: "(Verify Compute node network setting for MTU)",
    4: "(Verify Controller node network setting for MTU)",
    5: "(Verify Storage node network setting for MTU)"
}

ping_same_node_test_cases_dict = {
    6: "(Verify by pinging one Storage node to another with MTU 9000)",
    7: "(Verify by pinging one Controller node to another with MTU 9000)",
    8: "(Verify by pinging one Compute node to another with MTU 9000)"
}
feature_name = "MTU"

monthdict = {"01": "JAN", "02": "FEB" ,"03": "MAR", "04": "APR", "05": "MAY", "06": "JUNE", "07": "JULY",
             "08": "AUG", "09": "SEPT", "10": "OCT", "11": "NOV", "12": "DEC"}

# Noting starting time to check the elapsed time
start = time.time()

# making directory 'logs' if it does not exits
if not os.path.isdir("logs"):
    os.makedirs("logs")

# Noting starting time and date to name the log file
current = datetime.datetime.now().replace(second=0, microsecond=0)
name = str(datetime.datetime.strptime(str(current), "%Y-%m-%d %H:%M:%S")).split(" ")
out_file = feature_name + str(name[0].split("-")[2]) + monthdict[str(name[0].split("-")[1])] + \
           str(name[0].split("-")[0]) + "-" + str(name[1][:2]) + "-" + str(name[1][3:5])

# Logger configuration
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(message)s')
if not logger.handlers:
    timedRotatingFileHandler = logging.handlers.TimedRotatingFileHandler("logs/%s.log" % out_file, when='midnight',
                                                                         interval=1, backupCount=30)
    streamHandler = logging.StreamHandler()
    timedRotatingFileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    logger.addHandler(timedRotatingFileHandler)
    logger.addHandler(streamHandler)
    logger.setLevel(logging.INFO)
else:
    pass

cntl = {0: stamp_data["cntl0"], 1: stamp_data["cntl1"], 2: stamp_data["cntl2"]}
strg = {0: stamp_data["strg0"], 1: stamp_data["strg1"], 2: stamp_data["strg2"]}
cmpt = {0: stamp_data["cmpt0"], 1: stamp_data["cmpt1"], 2: stamp_data["cmpt2"]}
username_of_nodes = stamp_data["username_of_nodes"]

# # node IPs
# cntl_dict = {0: "192.168.120.143", 1: "192.168.120.133", 2: "192.168.120.137"}
# strg_dict = {0: "192.168.120.148", 1: "192.168.120.122", 2: "192.168.120.128"}
# cmpt_dict = {0: "192.168.120.127", 1: "192.168.120.123", 2: "192.168.120.129"}

# username of nodes
username_of_nodes = "heat-admin"

"""
Overcloud credentials

conn = connection.Connection(auth_url="http://192.168.24.16:5000//v3",
                             project_name="admin",
                             username="admin",
                             password="7Ekhk2rWaaXxukVc6eBWzcbAy",
                             domain_name="Default")
"""


# reading data from setup.json file
# if os.path.exists("setup.json"):
#     with open('setup.json') as data_file:
#         data = json.load(data_file)
#     static_flavor = str(data["flavor_name"])
#     static_image = str(data["image_name"])
#     static_sec_grp = str(data["secgroup_name"])
#     key_file_path = str(data["key_file_path"])
# else:
#     print ("\nFAILURE!!! setup.json file not found!!!\nUnable to execute script\n\n")
#     exit()

# nova list CLI command (execute after sourcing undercloudrc file)

def node_name_and_ip_from_nova_list():
    nodes_ip_dict = {}
    output = commands.getstatusoutput('nova list')
    # make dictionary of all nodes key-> name of node value-> ip of node nodes_dict
    for line in output[1].split("\n"):
        if "ctlplane" in str(line):
            ip = line.split("|")[6].split("=")[1].strip()
            node_name = line.split("|")[2].strip()
            nodes_ip_dict[node_name] = ip
    return nodes_ip_dict


# verifying communication between 2 storage/controller/compute nodes through ping with mtu size
def verify_by_ping_with_mtu_size(ip_of_node0, username_of_node0, ip_of_node1, packet_size):
    ssh_obj.ssh_to(logger, ip_of_node0, username_of_node0)
    flag = ssh_obj.ping_check_with_packet_size(logger, ip_of_node1, packet_size)
    ssh_obj.ssh_close()
    return flag


# Verify Compute node network setting for MTU
def test_case_3(cmpt_dict=cmpt):
    logger.info("\n==================================================================")
    logger.info("Executing Test Case 3 (Verify Compute node network setting for MTU)")
    logger.info("==================================================================")
    for node in cmpt_dict:
        ssh_obj.ssh_to(logger, cmpt_dict[node], username_of_nodes)
        logger.info ("\n>>>Verifying on Compute node%s IP:%s" % (node, cmpt_dict[node]))
        result_dict = ssh_obj.check_interface_name_and_mtu_size(logger)
        logger.info (">>>Output:")
        logger.info (result_dict)
        # check the names of nics and bonds through file: cat /proc/net/bond
        # insert code for verifying output:
        # put all the names in a list
        # pass/fail through list length
        ssh_obj.ssh_close()


# Verify Controller node network setting for MTU
def test_case_4(cntl_dict=cntl):
    logger.info("\n==================================================================")
    logger.info("Executing Test Case 4 (Verify Controller node network setting for MTU)")
    logger.info("==================================================================")
    for node in cntl_dict:
        ssh_obj.ssh_to(logger, cntl_dict[node], username_of_nodes)
        logger.info("\n>>>Verifying on Contoller node%s IP:%s" % (node, cntl_dict[node]))
        result_dict = ssh_obj.check_interface_name_and_mtu_size(logger)
        logger.info (">>>Output:")
        logger.info (result_dict)
        # check the names of nics and bonds through file: cat /proc/net/bond
        # insert code for verifying output:
        # put all the names in a list
        # pass/fail through list length
        ssh_obj.ssh_close()


# Verify Storage node network setting for MTU
def test_case_5(strg_dict=strg):
    logger.info("\n==================================================================")
    logger.info("Executing Test Case 5 (Verify Storage node network setting for MTU)")
    logger.info("==================================================================")
    # check name of storage node and replace "local-controller-0" with storage node
    for node in strg_dict:
        ssh_obj.ssh_to(logger, strg_dict[node], username_of_nodes)
        logger.info ("\n>>>Verifying on Storage node%s IP:%s" % (node, strg_dict[node]))
        result_dict = ssh_obj.check_interface_name_and_mtu_size(logger)
        logger.info (">>>Output:")
        logger.info (result_dict)
        # check the names of nics and bonds through file: cat /proc/net/bond
        # insert code for verifying output:
        # put all the names in a list
        # pass/fail through list length
        ssh_obj.ssh_close()


# Verify by pinging one Storage node to another with MTU 9000
def test_case_6(packet_size = 1500, strg_dict=strg):
    logger.info("\n===================================================================================")
    logger.info("Executing Test Case 6 (Verify by pinging one Storage node to another with MTU %s)" % packet_size)
    logger.info("===================================================================================")
    try:
        strg0_ip = strg_dict[0]
        for node in strg_dict:
            if strg_dict[node] != strg0_ip:
                logger.info (">>>Trying to ping Storage node%s from Storage node0...\n" % node)
                flag = verify_by_ping_with_mtu_size(strg0_ip, username_of_nodes,
                                                    strg_dict[node], packet_size)
                if flag:
                    logger.info ("\nTest Case 6 Passed, as Storage node0 is pinging the Storage node%s\n" % node)
                else:
                    logger.info ("\nTest Case 6 Failed! as Storage node0 is unable to ping the Storage node%s\n" % node)
    except:
        logger.info ("\nFailure: Unable to execute Test Case 6: \n(Verify by pinging one Storage node to another with MTU 9000)\n")


# Verify by pinging one Controller node to another with MTU 9000
def test_case_7(packet_size = 1500, cntl_dict=cntl):
    logger.info("\n======================================================================================")
    logger.info("Executing Test Case 7 (Verify by pinging one Controller node to another with MTU %s)"%packet_size)
    logger.info("======================================================================================")
    try:
        cntl0_ip = cntl_dict[0]
        for node in cntl_dict:
            if cntl_dict[node] != cntl0_ip:
                logger.info (">>>Trying to ping Controller node%s from Controller node0...\n" % node)
                flag = verify_by_ping_with_mtu_size(cntl0_ip, username_of_nodes,
                                                    cntl_dict[node], packet_size)
                if flag:
                    logger.info ("\nTest Case 7 Passed, as Controller node0 is pinging the Controller node%s\n" % node)
                else:
                    logger.info ("\nTest Case 7 Failed! as Controller node0 is unable to ping the Controller node%s\n" % node)
    except:
        logger.info ("\nFailure: Unable to execute Test Case 7: \n(Verify by pinging one Controller node to another with MTU 9000)\n")


# Verify by pinging one Compute node to another with MTU 9000
def test_case_8(packet_size = 1500, cmpt_dict=cmpt):
    logger.info("\n===================================================================================")
    logger.info("Executing Test Case 8 (Verify by pinging one Compute node to another with MTU %s)"%packet_size)
    logger.info("===================================================================================")
    try:
        cmpt0_ip = cmpt_dict[0]
        for node in cmpt_dict:
            if cmpt_dict[node] != cmpt0_ip:
                logger.info (">>>Trying to ping Compute node%s from Compute node0...\n" % node)
                flag = verify_by_ping_with_mtu_size(cmpt0_ip, username_of_nodes,
                                                    cmpt_dict[node], packet_size)
                if flag:
                    logger.info ("\nTest Case 8 Passed, as Compute node0 is pinging the Compute node%s\n" % node)
                else:
                    logger.info ("\nTest Case 6 Failed! as Compute node0 is unable to ping the Compute node%s\n" % node)
    except:
        logger.info ("\nFailure: Unable to execute Test Case 8: (Verify by pinging one Compute node to another with MTU 9000)\n")


# Creation and verification of Network
def test_case_9(network_name, cidr, subnet_name, gateway_ip, test_flag, delete_after_create_boolean):
    if test_flag:
        logger.info("\n===========================================================")
        logger.info("Executing Test Case 9 (Verify Network Creation on MTU 9000)")
        logger.info("===========================================================")
    else:
        pass
    network = creation_object.os_network_creation(logger, conn_create, network_name, cidr, subnet_name, gateway_ip)
    found_flag = creation_object.check_component_in_list(logger, conn_create, "network", network_name)
    if found_flag:
        if test_flag:
            logger.info ("\nTest Case 9 Passed, network: %s found in the network list.\n" % network_name)
        else:
            logger.info ("Network: %s created." % (network_name))
    else:
        if test_flag:
            logger.info ("\nTest Case 9 Failed! network: %s not found in the network list!\n" % network_name)
        else:
            logger.info ("Network: %s is not created!" % (network_name))
    if delete_after_create_boolean:
        logger.info ("Deleting the network: %s" % network_name)
        delete_object.os_delete_network_without_router(logger, conn_delete, network_name)
        return "deleted"
    else:
        logger.info ("Note: Network: %s is not deleted!" % network_name)
        return network


# Creation and verification of Instance
def test_case_10(server_name, network_name, flavor_name, image_name, secgroup_name, availability_zone,
                 test_flag, delete_after_create_boolean):
    if test_flag:
        logger.info ("\n==================================================================")
        logger.info ("Executing Test Case 10 (Verify instance creation on MTU size 9000)")
        logger.info ("==================================================================")
    else:
        pass
    network_is_already_created = creation_object.check_component_in_list(logger, conn_create, "network", network_name)
    ret_server_flag = 0
    if network_is_already_created:
        server = creation_object.os_server_creation(logger, conn_create, server_name, flavor_name, image_name, network_name,
                                                    secgroup_name, availability_zone)
        time.sleep(2)
        flag = creation_object.check_component_in_list(logger, conn_create, "server", server_name)
        if flag:
            if test_flag:
                logger.info ("\nTest Case 10 Passed, instance: %s found in the server list.\n" % server_name)
            else:
                logger.info ("Instance: %s created." % (server_name))
            ret_server_flag = 1
        else:
            if test_flag:
                logger.info ("\nTest Case 10 Failed! instance: %s not found in the server list!\n" % server_name)
            else:
                logger.info ("Instance: %s is not created!")
    else:
        logger.info ("Failure: Network: %s not found in network list!")
    if delete_after_create_boolean:
        logger.info ("Deleting the instance: %s" % server_name)
        delete_object.os_delete_server(logger, conn_delete, server_name)
        return "deleted"
    else:
        logger.info ("Note: Server: %s is not deleted!" % server_name)
        if ret_server_flag:
            return server


# Creation and verification of Router
def test_case_11(router_name, port_name, network_name, test_flag, delete_after_create_boolean):
    if test_flag:
        logger.info ("\n================================================================")
        logger.info ("Executing Test Case 11 (Verify router creation on MTU size 9000)")
        logger.info ("================================================================")
    else:
        pass
    network_is_already_created = creation_object.check_component_in_list(logger, conn_create, "network", network_name)
    router = None
    if network_is_already_created:
        router = creation_object.os_router_creation(logger, conn_create, router_name, port_name, network_name)
        flag = creation_object.check_component_in_list(logger, conn_create, "router", router_name)
        if flag:
            logger.info ("\nTest Case 11 Passed, router: %s found in the router list.\n" % router_name)
        else:
            logger.info ("\nTest Case 11 Failed! router: %s not found in the router list!" % router_name)
    if delete_after_create_boolean:
        logger.info ("Deleting the router: %s" % router_name)
        delete_object.os_deleting_router_with_1_network(logger, conn_delete, network_name, router_name, port_name)
        return None
    else:
        logger.info ("Note: Router: %s is not deleted!" % router_name)
        return router


# Creation and verification of Floating IP
def test_case_12(server_name):
    logger.info ("\n=====================================================================")
    logger.info ("Executing Test Case 12 (Verify floating ip creation on MTU size 9000)")
    logger.info ("=====================================================================")
    floating_ip = creation_object.os_floating_ip_creation_assignment(logger, conn_create, server_name)
    ip = conn_create.get_server(server_name).public_v4
    p_flag = 0
    if floating_ip.floating_ip_address == ip:
        logger.info("Floating IP Assigned Successfully")
        p_flag = 1
    else:
        logger.info("Floating IP assignment Failed!!!")
        p_flag = 0
    if p_flag == 1:
        logger.info ("\nTest Case 12 Passed.\n")
    else:
        logger.info ("\nTest Case 12 Failed!\n")



# Creation and verification of Network,Instance,Router,Floating IP
def test_cases_9_to_12(delete_after_create_flag):
    try:
        # test_case_9("f_net", "192.168.40.0/24", "sub_f_net", "192.168.40.1", True, False)
        # test_case_10("fz_vm", "last", "last", "centos", "last", True, False)
        # test_case_11("f_router", "f_port", "f_net", False)
        # test_case_12("fz_vm")
        test_case_9(network_name=data["network_name"], cidr=data["cidr"], subnet_name=data["subnet_name"],
                    gateway_ip=data["gateway_ip"], test_flag=True, delete_after_create_boolean=False)
        test_case_10(server_name=data["server_name"], network_name=data["network_name"],
                     flavor_name=data["static_flavor"],
                     image_name=data["static_image"], secgroup_name=data["static_secgroup"],
                     availability_zone=data["zone1"],
                     test_flag=True, delete_after_create_boolean=False)
        test_case_11(router_name=data["router_name"], port_name=data["port_name"], network_name=data["network_name"],
                     test_flag=True, delete_after_create_boolean=False)
        test_case_12(server_name=data["server_name"])
        if delete_after_create_flag:
            delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])
            delete_object.os_deleting_router_with_1_network(logger, conn_delete, network_name=data["network_name"],
                                                            router_name=data["router_name"],
                                                            port_name=data["port_name"])
            delete_object.os_delete_detached_floating_ips(logger, conn_delete)
    except:
        logger.info ("\nError encountered while executing Test Case: 17!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])
        delete_object.os_deleting_router_with_1_network(logger, conn_delete, network_name=data["network_name"],
                                                        router_name=data["router_name"], port_name=data["port_name"])
        delete_object.os_delete_detached_floating_ips(logger, conn_delete)


def initialize_ping_check_from_namespace(ips_list, network_name, image_name, ping_check=True):
    instance1_private_ip = ips_list[0]
    instance2_private_ip = ips_list[1]
    namespace_id = creation_object.get_network_namespace_id(logger, conn_create, network_name)
    ssh_obj.ssh_to(logger, cntl[0], username_of_nodes)
    key_file_name = data["key_file_path"].split("/")[3]
    destination_path = "/home/%s/%s" % (username_of_nodes, key_file_name)
    ssh_obj.send_key_if_not_present(logger, destination_path)
    time.sleep(20)
    if ping_check is False:
        return namespace_id, destination_path
    else:
        out = ssh_obj.ping_check_from_namespace(logger, namespace_id, instance1_private_ip, image_name, destination_path,
                                                instance2_private_ip)
        ssh_obj.ssh_close()
        return out


# Verify Communication (through ping check) between 2 Instances on Same Compute and Same Tenant Network
def test_case_13(server1_name=data["server1_name"], server2_name=data["server2_name"],
                 network_name=data["network_name"],
                 subnet_name=data["subnet_name"], router_name=data["router_name"], port_name=data["port_name"],
                 zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"], flavor_name=data["static_flavor"],
                 image_name=data["static_image"], secgroup_name=data["static_secgroup"], assign_floating_ip=False,
                 delete_after_create_flag=True):
    logger.info("\n================================================================")
    logger.info("Executing Test Case 13 (Verify Communication between 2 Instances")
    logger.info (" on Same Compute and Same Tenant Network)")
    logger.info("================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_same_network(logger, conn_create, server1_name,
                                                                                   server2_name, network_name,
                                                                                   subnet_name,
                                                                                   router_name, port_name, zone, cidr,
                                                                                   gateway_ip, flavor_name, image_name,
                                                                                   secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        out = initialize_ping_check_from_namespace(ips_list, network_name, image_name)
        # if out is True:
        #     print "Test Case 13 Passed. Communication successful."
        # elif out is False:
        #     print "Test Case 13 Failed! Communication unsuccessful!"
        # else:
        #     print "Unable to connect to instance."
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name, router_name, port_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 13!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name,
                                                                   server2_name, network_name, router_name, port_name)


def test_case_14(server1_name=data["server1_name"], server2_name=data["server2_name"], network_name=data["network_name"],
                 subnet_name=data["subnet_name"], router_name=data["router_name"], port_name=data["port_name"],
                 zone1=data["zone1"], zone2=data["zone2"], cidr=data["cidr"], gateway_ip=data["gateway_ip"],
                 flavor_name=data["static_flavor"], image_name=data["static_image"], secgroup_name=data["static_secgroup"],
                 assign_floating_ip=False, delete_after_create_flag=True):
    logger.info("\n================================================================")
    logger.info("Executing Test Case 14 (Verify Communication between 2 Instances")
    logger.info (" on Different Compute and Same Tenant Network)")
    logger.info("================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_dif_compute_same_network(logger, conn_create, server1_name, server2_name,
                                                      network_name, subnet_name,
                                                      router_name, port_name, zone1 ,zone2, cidr,
                                                      gateway_ip, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        out = initialize_ping_check_from_namespace(ips_list, network_name, image_name)
        # if out is True:
        #     print "Test Case 14 Passed. Communication successful."
        # else:
        #     print "Test Case 14 Failed! Communication unsuccessful!"

        ssh_obj.ssh_close()
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name,
                                                                       router_name, port_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 14!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                   network_name,
                                                                   router_name, port_name)


def test_case_15(server1_name=data["server1_name"], server2_name=data["server2_name"],
                 network1_name=data["network1_name"],
                 network2_name=data["network2_name"], subnet1_name=data["subnet1_name"],
                 subnet2_name=data["subnet2_name"],
                 router_name=data["router_name"], port1_name=data["port1_name"], port2_name=data["port2_name"],
                 zone1=data["zone1"], zone2=data["zone2"], cidr1=data["cidr1"], cidr2=data["cidr2"],
                 gateway_ip1=data["gateway_ip1"], gateway_ip2=data["gateway_ip2"], flavor_name=data["static_flavor"],
                 image_name=data["static_image"], secgroup_name=data["static_secgroup"], assign_floating_ip=False,
                 delete_after_create_flag=True):
    logger.info("\n================================================================")
    logger.info("Executing Test Case 15 (Verify Communication between 2 Instances")
    logger.info (" on Different Compute and Different Tenant Network)")
    logger.info("================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_dif_compute_dif_network(logger, conn_create, server1_name,
                                                                                 server2_name, network1_name,
                                                                                 network2_name,
                                                                                 subnet1_name, subnet2_name,
                                                                                 router_name, port1_name, port2_name,
                                                                                 zone1, zone2, cidr1,
                                                                                 gateway_ip1, cidr2, gateway_ip2,
                                                                                 flavor_name, image_name,
                                                                                 secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        out = initialize_ping_check_from_namespace(ips_list, network1_name, image_name)
        # if out is True:
        #     print "Test Case 15 Passed. Communication successful."
        # else:
        #     print "Test Case 15 Failed! Communication unsuccessful!"
        ssh_obj.ssh_close()
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                        network1_name,
                                                                        network2_name, router_name, port1_name,
                                                                        port2_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 15!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                    network1_name,
                                                                    network2_name, router_name, port1_name, port2_name)


def test_case_16(server1_name=data["server1_name"], server2_name=data["server2_name"],
                 network1_name=data["network1_name"],
                 network2_name=data["network2_name"], subnet1_name=data["subnet1_name"],
                 subnet2_name=data["subnet2_name"],
                 router_name=data["router_name"], port1_name=data["port1_name"], port2_name=data["port2_name"],
                 zone=data["zone1"], cidr1=data["cidr1"], cidr2=data["cidr2"],
                 gateway_ip1=data["gateway_ip1"], gateway_ip2=data["gateway_ip2"], flavor_name=data["static_flavor"],
                 image_name=data["static_image"], secgroup_name=data["static_secgroup"], assign_floating_ip=False,
                 delete_after_create_flag=True):
    logger.info("\n================================================================")
    logger.info("Executing Test Case 16 (Verify Communication between 2 Instances")
    logger.info (" on Same Compute and on Different Tenant Network)")
    logger.info("================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_dif_network(logger, conn_create, server1_name,
                                                                                  server2_name, network1_name,
                                                                                  network2_name,
                                                                                  subnet1_name, subnet2_name,
                                                                                  router_name, port1_name, port2_name,
                                                                                  zone, cidr1,
                                                                                  gateway_ip1, cidr2, gateway_ip2,
                                                                                  flavor_name, image_name,
                                                                                  secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        out = initialize_ping_check_from_namespace(ips_list, network1_name, image_name)
        # if out is True:
        #     logger.info "Test Case 16 Passed. Communication successful."
        # else:
        #     logger.info "Test Case 16 Failed! Communication unsuccessful!"
        ssh_obj.ssh_close()
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                        network1_name, network2_name,
                                                                        router_name, port1_name, port2_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 16!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                    network1_name,
                                                                    network2_name, router_name, port1_name, port2_name)


# Verify Performance with Iperf3 between 2 Instances on Same Compute and Same Tenant Network
def test_case_17():
    logger.info("\n===============================================================")
    logger.info("Executing Test Case 17 (Verify Performance with Iperf3 between ")
    logger.info (" 2 Instances on Same Compute and Same Tenant Network)")
    logger.info("===============================================================")
    try:
        bandwidth = iperf3_funcs.create_2_instances_on_same_compute_same_network_and_exec_iperf3()
    except:
        logger.info ("\nError encountered while executing test case 17!\n")


# Verify Performance with Iperf3 between 2 Instances on Different Compute and Same Tenant Network
def test_case_18():
    logger.info("\n==============================================================")
    logger.info("Executing Test Case 18 (Verify Performance with Iperf3 between")
    logger.info (" 2 Instances on Different Compute and Same Tenant Network)")
    logger.info("==============================================================")
    try:
        pdb.set_trace()
        bandwidth = iperf3_funcs.create_2_instances_on_diff_compute_same_network_and_exec_iperf3()
    except:
        logger.info ("\nError encountered while executing test case 18!\n")


# Verify Performance with Iperf3 between 2 Instances on Different Compute and Different Tenant Network
def test_case_19():
    logger.info("\n==============================================================")
    logger.info("Executing Test Case 19 (Verify Performance with Iperf3 between")
    logger.info(" 2 Instances on Different Compute and Different Tenant Network)")
    logger.info("==============================================================")
    # Create two instances on different compute and different tenant network
    try:
        bandwidth = iperf3_funcs.create_2_instances_on_diff_compute_diff_network_and_exec_iperf3()
    except:
        logger.info ("\nError encountered while executing test case 19!\n")


# Verify Performance with Iperf3 between 2 Instances on Same Compute and on Different Tenant Network
def test_case_20():
    logger.info("\n==============================================================")
    logger.info("Executing Test Case 20 (Verify Performance with Iperf3 between")
    logger.info(" 2 Instances on Same Compute and on Different Tenant Network)")
    logger.info("==============================================================")
    # Create two instances on different compute and different tenant network
    try:
        bandwidth = iperf3_funcs.create_2_instances_on_same_compute_diff_network_and_exec_iperf3()
    except:
        logger.info ("Error encountered while executing test case 20!")


def test_case_21(packet_size=10000):
    logger.info ("\n==============================================================")
    logger.info ("Executing Test Case 21 (Verify that compute,controller and ")
    logger.info ("storage nodes are not able to ping on frames higher than 9000)")
    logger.info ("==============================================================")
    try:
        pass_count = 0
        for i in range(0,3):
            ssh_obj.ssh_to(logger, cmpt[i], username_of_nodes)
            for j in range(0,3):
                p_flag = ssh_obj.ping_check_with_packet_size(logger, cntl[j], packet_size)
                if p_flag is True:
                    logger.info ("Compute node%s is able to ping Controller node%s with packet size %s." % (i, j, packet_size))
                    pass_count +=1
                else:
                    logger.info ("Compute node%s is unable to ping Controller node%s with packet size %s." % (i, j, packet_size))
                p_flag1 = ssh_obj.ping_check_with_packet_size(logger, strg[j], packet_size)
                if p_flag1 is True:
                    pass_count +=1
                    logger.info ("Compute node%s is able to ping Storage node%s with packet size %s." % (i, j, packet_size))
                else:
                    logger.info ("Compute node%s is unable to ping Storage node%s with packet size %s." % (i, j, packet_size))
            ssh_obj.ssh_close()
        logger.info ("\n")
        logger.info (pass_count)
        logger.info ("\n")
    except:
        logger.info ("\nError encountered while executing Test Case: 21!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


def test_case_22(packet_size, server1_name=data["server1_name"], server2_name=data["server2_name"],
                 network_name=data["network_name"], subnet_name=data["subnet_name"], router_name=data["router_name"],
                 port_name=data["port_name"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"],
                 flavor_name=data["static_flavor"], image_name=data["static_image"], secgroup_name=data["static_secgroup"],
                 assign_floating_ip=False, delete_after_create_flag=True):
    logger.info ("\n=============================================================")
    logger.info ("Executing Test Case 22 (Verify that instances are not able to")
    logger.info (" ping on frames higher than 9000")
    logger.info ("=============================================================")
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_same_network(logger, conn_create, server1_name,
                                                                                   server2_name, network_name,
                                                                                   subnet_name,
                                                                                   router_name, port_name, zone, cidr,
                                                                                   gateway_ip, flavor_name, image_name,
                                                                                   secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        out = initialize_ping_check_from_namespace(ips_list, network_name, image_name)
        if out is False:
            logger.info ("\nTest Case 22 Passed. Communication unsuccessful with packet size %s.\n" % packet_size)
        else:
            logger.info ("\nTest Case 22 Failed! Communication successful with packet size %s!\n" % packet_size)
        ssh_obj.ssh_close()
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name, router_name, port_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 22!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name,
                                                                   server2_name, network_name, router_name, port_name)


def test_case_23(packet_size_list=None, server1_name=data["server1_name"], server2_name=data["server2_name"],
                 network_name=data["network_name"], subnet_name=data["subnet_name"], router_name=data["router_name"],
                 port_name=data["port_name"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"],
                 flavor_name=data["static_flavor"], image_name=data["static_image"], secgroup_name=data["static_secgroup"],
                 assign_floating_ip=False, delete_after_create_flag=True):
    logger.info ("\n=====================================================================")
    logger.info ("Executing Test Case 23 (Verify that instances are able to communicate")
    logger.info ("with eachother on lower MTU sizes i-e 64,128,512,1500,3000,4000,6000")
    logger.info ("=====================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_same_network(logger, conn_create, server1_name,
                                                                                   server2_name, network_name,
                                                                                   subnet_name,
                                                                                   router_name, port_name, zone, cidr,
                                                                                   gateway_ip, flavor_name, image_name,
                                                                                   secgroup_name, assign_floating_ip)
        logger.info ("Two instances Created Successfully.")
        namespace_id, destination_path = initialize_ping_check_from_namespace(ips_list, network_name, image_name, ping_check=False)
        instance1_private_ip = ips_list[0]
        instance2_private_ip = ips_list[1]
        if packet_size_list is None:
            packet_size_list = [64,128,512,1500,3000,4000,6000]
        else:
            pass
        count = 0
        for packet_size in packet_size_list:
            logger.info ("\nChecking for packet size: %s" % packet_size)
            out = ssh_obj.ping_check_from_namespace(logger, namespace_id, instance1_private_ip, image_name, destination_path,
                                                    instance2_private_ip, packet_size)
            if out is True:
                logger.info ("Communication successful with packet size %s." % packet_size)
                count += 1
            else:
                logger.info ("Communication unsuccessful with packet size %s!" % packet_size)
        if count == len(packet_size_list):
            logger.info ("\nTest Case 23 Passed. Communication successful with all packet sizes %s.\n" % packet_size_list)
        else:
            logger.info ("\nTest Case 23 Failed! Communication unsuccessful with all or some packet sizes. Scroll up to " \
                  "see the details.\n" % packet_size_list)
        ssh_obj.ssh_close()
        if delete_after_create_flag:
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name, router_name, port_name)
    except:
        logger.info ("\nError encountered while executing Test Case: 23!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name,
                                                                   server2_name, network_name, router_name, port_name)



def test_case_24():
    logger.info ("\n=========================================================================")
    logger.info ("Executing Test Case 24 (Verify that compute ,controller and storage nodes"
           " are able to communicate with each other on lower MTU sizes i-e 64,128,512,1500,3000,4000,6000")
    logger.info ("=========================================================================")
    try:
        packet_size_list = [64, 128, 512, 1500, 3000, 4000, 6000]
        pass_count = 0
        for i in range(0,3):
            ssh_obj.ssh_to(logger, cmpt[i], username_of_nodes)
            for j in range(0,3):
                for packet_size in packet_size_list:
                    p_flag = ssh_obj.ping_check_with_packet_size(logger, cntl[j], packet_size)
                    if p_flag is True:
                        logger.info ("Compute node%s is able to ping Controller node%s with packet size %s." % (i, j, packet_size))
                        pass_count +=1
                    else:
                        logger.info ("Compute node%s is unable to ping Controller node%s with packet size %s." % (i, j, packet_size))
                    p_flag1 = ssh_obj.ping_check_with_packet_size(logger, strg[j], packet_size)
                    if p_flag1 is True:
                        pass_count +=1
                        logger.info ("Compute node%s is able to ping Storage node%s with packet size %s." % (i, j, packet_size))
                    else:
                        logger.info ("Compute node%s is unable to ping Storage node%s with packet size %s." % (i, j, packet_size))
            ssh_obj.ssh_close()
        logger.info ("\n")
        logger.info (pass_count)
        logger.info ("\n")
    except:
        logger.info ("\nError encountered while executing Test Case: 24!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


# server1_name = "t_vm1"
# server2_name = "t_vm2"
# network_name = "t_net"
# network1_name = "t_net1"
# network2_name = "t_net2"
# subnet_name = "t_snet"
# subnet1_name = "t_snet1"
# subnet2_name = "t_snet2"
# router_name = "t_router"
# port_name = "t_port"
# port1_name = "t_port1"
# port2_name = "t_port2"
# zone = zone1 = zone2 = "sriov-zone"
# cidr = "192.168.40.0/24"
# gateway_ip = "192.168.40.1"
# cidr1 = "192.168.30.0/24"
# gateway_ip1 = "192.168.30.1"
# cidr2 = "192.168.20.0/24"
# gateway_ip2 = "192.168.20.1"
# assign_floating_ip = True
# delete_after_create_flag = True





# test_case_13(server1_name, server2_name, network_name, subnet_name, router_name, port_name, zone, cidr,gateway_ip,
#                                 flavor_name, image_name, secgroup_name, assign_floating_ip, delete_after_create_flag)

# test_case_17(server1_name, server2_name, network_name, subnet_name, router_name, port_name, zone, cidr,
#                                            gateway_ip, assign_floating_ip, delete_after_create_flag)

# test_case_18(server1_name, server2_name, network_name, subnet_name, router_name, port_name, zone1, zone2,
#                                                       cidr, gateway_ip, assign_floating_ip, delete_after_create_flag)

# test_case_19(server1_name, server2_name, network1_name, network2_name, subnet1_name, subnet2_name, router_name,
#                             port1_name, port2_name, zone1, zone2, cidr1, gateway_ip1, cidr2, gateway_ip2,
#                             assign_floating_ip, delete_after_create_flag)

# test_case_20(server1_name, server2_name, network1_name, network2_name, subnet1_name, subnet2_name, router_name,
#                                                             port1_name, port2_name, zone, cidr1, gateway_ip1,
#                                                         cidr2, gateway_ip2, assign_floating_ip, delete_after_create_flag)


# test_case_17()
# test_case_3()
# test_case_4()
# test_case_5()
# 
# test_case_6(1470)
# test_case_7(1470)
# test_case_8(1470)
# test_cases_9_to_12(True)

# test_case_17()
# test_case_18()

# test_case_13()

"""
if __name__ == '__main__':
    # NOTE: "nova list" command will be executed on undercloud
    output = commands.getstatusoutput('nova list')
    nodes_ip_dict = {}
    # make dictionary of all nodes key-> name of node value-> ip of node nodes_dict
    for line in output[1].split("\n"):
        if "ctlplane" in str(line):
            ip = line.split("|")[6].split("=")[1].strip()
            node_name = line.split("|")[2].strip()
            nodes_ip_dict[node_name] = ip
    name_of_compute_node = "overcloud-compute-0"
    name_of_controller_node = "overcloud-controller-1"
    # name_of_storage_node = "overcloud-storage-1"
    ip_of_compute_node = nodes_ip_dict[name_of_compute_node]
    ip_of_controller_node = nodes_ip_dict[name_of_controller_node]
    # ip_of_storage_node = nodes_ip_dict[name_of_storage_node]
    # user_name = username_of_nodes

"""
# test_case_3()
# test_case_5()
# test_case_6(packet_size=1400)
# test_case_7(packet_size=1400)
# test_case_8(packet_size=1400)
# test_cases_9_to_12(True)
# test_case_9()
# test_case_10()
# test_case_11()
# test_case_12()
test_case_13()
test_case_14()
test_case_15()
test_case_16()

test_case_17()
test_case_18()

test_case_19()

test_case_20()

test_case_21()

test_case_22(packet_size=1400)

test_case_23()
