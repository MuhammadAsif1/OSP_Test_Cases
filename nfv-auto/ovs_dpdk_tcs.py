import sys
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import iperf3_funcs as iperf3
import pdb
import time
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import paramiko

ssh_obj = ssh_functions()
creation_object = Os_Creation_Modules()
delete_object = Os_Deletion_Modules()

conn_create = creation_object.os_connection_creation()
conn_delete = delete_object.os_connection_creation()

cntl = {0: stamp_data["cntl0"], 1: stamp_data["cntl1"], 2: stamp_data["cntl2"]}
strg = {0: stamp_data["strg0"], 1: stamp_data["strg1"], 2: stamp_data["strg2"]}
cmpt = {0: stamp_data["cmpt0"], 1: stamp_data["cmpt1"], 2: stamp_data["cmpt2"]}
username_of_nodes = stamp_data["username_of_nodes"]
sah_node_ip = stamp_data["sah_node_ip"]
sah_node_username = stamp_data["sah_node_username"]
sah_node_password = stamp_data["sah_node_password"]
csp_profile_ini_file_path = stamp_data["csp_profile_ini_file_path"]

feature_name = "OVSDPDK"

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


def initialize_ping_check_from_namespace(ips_list, network_name, image_name, ping_check=True):
    instance1_private_ip = ips_list[0]
    instance2_private_ip = ips_list[1]
    namespace_id = creation_object.get_network_namespace_id(logger, conn_create, network_name)
    ssh_obj.ssh_to(logger, cntl[0], username_of_nodes)
    key_file_name = data["key_file_path"].split("/")[3]
    destination_path = "/home/%s/%s" % (username_of_nodes, key_file_name)
    ssh_obj.send_key_if_not_present(logger, destination_path)
    # if image_name == "cirros":
    #     print "Waiting for 10 seconds..."
    #     time.sleep(10)
    # elif image_name == "centos":
    #     print "Waiting for 20 seconds..."
    #     time.sleep(20)
    # else:
    #     time.sleep(20)
    time.sleep(10)
    if ping_check is False:
        return namespace_id, destination_path
    else:
        out = ssh_obj.ping_check_from_namespace(logger, namespace_id, instance1_private_ip, image_name, destination_path,
                                                instance2_private_ip)
        ssh_obj.ssh_close()
        return out


def check_huge_page_size_from(ip_of_node, username):
    huge_pages_size = ""
    ssh_obj.ssh_to(logger, ip_of_node, username)
    output = ssh_obj.execute_command_return_output(logger, "cat /proc/meminfo | grep Huge")
    for line in output.split("\n"):
        if "Hugepagesize" in line:
            huge_pages_size = line.split(":")[1].strip()
        else:
            pass
    ssh_obj.ssh_close()
    return huge_pages_size

"""
def create_instance_with_dpdk_flavor(assign_floating_ip, server_name=data["server_name"],
                                     flavor_name=data["ovsdpdk_flavor"]):

    #flavor = create_ovs_dpdk_flavor(flavor_name, ram_size, no_of_vcpus, disk_size)
    creation_object.os_network_creation(logger, conn_create, data["static_network"], data["static_cidr"], data["static_subnet"], data["static_gateway"])
    creation_object.os_router_creation(logger, conn_create, data["static_router"], data["static_port"], data["static_network"])

    if assign_floating_ip is True:
        server_munch = creation_object.os_server_creation_with_floating_ip(logger, conn_create, server_name=server_name,
                                                                           flavor_name=flavor_name,
                                                                           image_name=data["static_image"],
                                                                           network_name=data["static_network"],
                                                                           secgroup_name=data["static_secgroup"],
                                                                           availability_zone=data["zone1"])
    else:
        server_munch = creation_object.os_server_creation(logger, conn_create, server_name=server_name,
                                                          flavor_name=flavor_name,
                                                          image_name=data["static_image"],
                                                          network_name=data["static_network"],
                                                          secgroup_name=data["static_secgroup"],
                                                          availability_zone=data["zone1"])
    logger.info("Instance Created.")
    return server_munch


def create_ovs_dpdk_flavor():
    flavor = creation_object.os_flavor_ovsdpdk_creation(logger, conn_create, name=data["ovsdpdk_flavor"], ram=4096, vcpus=4,
                                                        disk=40)
    return flavor
"""

# Validates the OVS DPDK works fine with floating IP
'''def test_case_3():
    logger.info("\n==========================================================================")
    logger.info("Executing Test Case 3 (Validates the OVS DPDK works fine with floating IP)")
    logger.info("==========================================================================")
    try:
        # pdb.set_trace()
        # server_munch = creation_object.os_server_creation(conn_create, server_name=data["server_name"],
        #                                             flavor_name=data["ovsdpdk_flavor"],
        #                                    image_name=data["static_image"], network_name=data["static_network"],
        #                                    secgroup_name=data["static_secgroup"], availability_zone=data["zone1"],
        #                                                   key_name=data["key_name"])
        # f_ip_munch = creation_object.os_floating_ip_creation_assignment(conn_create, server_name=data["server_name"])
        # flt_ip = str(f_ip_munch.floating_ip_address)
        pdb.set_trace()
        #server_munch = self.create_instance_with_dpdk_flavor(self, assign_floating_ip=False)
        # pdb.set_trace()
        flt_ip = server_munch[1]
        # pdb.set_trace()
        logger.info("Getting the gateway of floating ip...")
        subnet_id_list = conn_create.get_network(data["public_network"]).subnets
        for s_id in subnet_id_list:
            gateway_floating_ip = conn_create.get_subnet(str(s_id)).gateway_ip
            break
        logger.info("Gateway of floating ip: %s" % gateway_floating_ip)
        # pdb.set_trace()
        time.sleep(10)
        ssh_obj.ssh_to(logger, flt_ip, data["static_image"], key_file_name=data["key_file_path"])
        logger.info("Trying to ping the gateway through instance..")
        flag = ssh_obj.simple_ping_check(logger, str(gateway_floating_ip))
        # pdb.set_trace()
        # logger.info(flag)
        if flag:
            logger.info("\nTest Case 3 Passed, Ping successful.\n")
        else:
            logger.info("\nTest Case 3 Failed! Ping unsuccessful!\n")
        ssh_obj.ssh_close()
        # Deleting instance after test execution
        delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])

        delete_object.os_deleting_router_with_1_network(self, logger, conn_delete, data["static_network"], data["static_router"], data["static_port"])
    except:
        delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])
        delete_object.os_deleting_router_with_1_network(self, logger, conn_delete, data["static_network"], data["static_router"], data["static_port"])

        logger.info ("\nError encountered while executing Test Case: 3!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno)) 
'''
def test_case_3(flavor_name, availability_zone, image_name, port_name, server_name, secgroup_name, network_name, router_name, subnet_name, cidr, gateway, deleteall=True):
               
    try:
        # flavor = creation_object.os_flavor_ovsdpdk_creation(logger, conn_create, name=flavor_name,
        #                                            ram=4096, vcpus=6, disk=40)
        output = creation_object.os_create_dpdk_enabled_instance(logger, conn_create, network_name=network_name, port_name=port_name, router_name=router_name, subnet_name=subnet_name, cidr=cidr, gateway=gateway, flavor_name=flavor_name, availability_zone=availability_zone, image_name=image_name, server_name=server_name, security_group_name=secgroup_name)
        time.sleep(10)
        ping = ssh_obj.locally_ping_check(logger, ip=output[2][1])
        if ping:
            logger.info ("Test 3 SUCCESSFUL")
        else:
            logger.info ("Test 3 FAILED")
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")

        return output


    except:
        logger.info ("Unable to execute test case 3")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
 ######################################################################################   
def test_case_4(flavor_name, availability_zone, image_name, port_name, server_name, secgroup_name, network_name, router_name, subnet_name, cidr, gateway, cmpt0, cmpt1, cmpt2, deleteall=True):
    logger.info("\n=====================================================================================")
    logger.info("Executing Test Case 4 (Validate Hugepages are enabled and working fine with OVS DPDK)")
    logger.info("=====================================================================================")
    #compute_node_ips_list = "192.168.120.141"
    try:
        #huge_page_sizes_list = []
        #for node in cmpt_dict:
            #huge_page_size = check_huge_page_size_from(cmpt_dict[node], username_of_nodes)
            #huge_page_sizes_list.append(huge_page_size)
        # flavor = create_ovs_dpdk_flavor(flavor_name=data["ovsdpdk_flavor"])

        #server_munch = create_instance_with_dpdk_flavor(assign_floating_ip=False, server_name=data["server_name"])
        output = creation_object.os_create_dpdk_enabled_instance(logger, conn_create, network_name=network_name, port_name=port_name, router_name=router_name, subnet_name=subnet_name, cidr=cidr, gateway=gateway, flavor_name=flavor_name, availability_zone=availability_zone, image_name=image_name, server_name=server_name, security_group_name=secgroup_name)
        time.sleep(10)
        ping = ssh_obj.locally_ping_check(logger, ip=output[2][1])
        if ping:
            #################################################
            ### this 'hugespages_check(nova)' will go into compute node and will check hugepages count from /proc/meminfo, should be hugepages=1048576 
            def hugepages_check(nova):
                client=paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(nova, username='heat-admin')
                def command_function(com):
                    output=""
                    stdin, stdout, stderr = client.exec_command(com)
                    stdout=stdout.readlines()
                    for line in stdout:
                        output=output+line
                    return output

                com="grep 'Huge' /proc/meminfo"
                y=command_function(com)
                x=os.popen("echo '%s' | awk '/Hugepagesize/ {print $2}' "% y).read()
                hpsize="1048576"
                sl = len(hpsize)
                hugepages = x[:sl]
                if hugepages==hpsize:
                   print('Hugepages : %s'% hpsize)
                   print('===============Test Case Executed Successfully on %s ================='% nova)
                else:
                   print('=============== Test Case Failed on %s ================'% nova)
                   
            hugepages_check(cmpt0)
            hugepages_check(cmpt1)
            hugepages_check(cmpt2)
                
            #################################################
        else:
            logger.info ("Test 4 FAILED")
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")

        return output


    except:
        logger.info ("\nError encountered while executing Test Case: 4 !")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
###############################################################################################################
def test_case_5(flavor_name, availability_zone, image_name, port_name, server_name, secgroup_name, network_name, router_name, subnet_name, cidr, gateway, cmpt0, cmpt1, cmpt2, deleteall=True):

    logger.info("\n==============================================================================================")
    logger.info("Executing Test Case 5 (Validate Numa is enabled and CPU pinning is working fine with OVS DPDK)")
    logger.info("==============================================================================================")
    try:
        # create_ovs_dpdk_flavor()
        # pdb.set_trace()
        #server_munch = create_instance_with_dpdk_flavor(assign_floating_ip=True, server_name=data["server_name"])
        #logger.info("Instance Created.")
        # pdb.set_trace()
        # time.sleep(22)
        output = creation_object.os_create_dpdk_enabled_instance(logger, conn_create, network_name=network_name, port_name=port_name, router_name=router_name, subnet_name=subnet_name, cidr=cidr, gateway=gateway, flavor_name=flavor_name, availability_zone=availability_zone, image_name=image_name, server_name=server_name, security_group_name=secgroup_name)
        time.sleep(10)
        ping = ssh_obj.locally_ping_check(logger, ip=output[2][1])
        if ping:
            logger.info ("Test 3 SUCCESSFUL")
        else:
            logger.info ("Test 3 FAILED")
        ###################################################################################
        server_id = str(conn_create.get_server(data["server_name"]).id)#str(server_munch.id)
        command = "sudo virsh dumpxml %s" % server_id
        ssh_obj.ssh_to(logger, cmpt[0], username_of_nodes)
        logger.info("Executing command: %s on Compute: %s" %(command, cmpt[0]))
        output = ssh_obj.execute_command_return_output(logger, command)
        logger.info (output)
        logger.info ("Need to add the test case pass fail criteria!!!")
        
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")

        return output
        # run virsh dumpxml <instance_id> on compute where instance is provisioned
        # delete both ; instance and flavor

        #delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])
        #delete_object.os_deleting_router_with_1_network(self, logger, conn, data["static_network"], data["static_router"], data["static_port"])

    except:
        logger.info ("Error encountered while executing Test Case: 5 !")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name, network_name=network_name, router_name=router_name, port_name=port_name)
        #delete_object.os_delete_server(logger, conn_delete, server_name=data["server_name"])
        #delete_object.os_deleting_router_with_1_network(self, logger, conn, data["static_network"], data["static_router"], data["static_port"])

        # delete_object.os_deleting_flavor(conn_delete, data["flavor_name"]

# def test_case_6():
#     print("=====================================================================================")
#     print("Executing Test Case 6 (Validate virtual NICs on instance remains intact after reboot)")
#     print("=====================================================================================")
#     try:
#         pdb.set_trace()
#         server_munch = create_instance_with_dpdk_flavor(assign_floating_ip=True, server_name=data["server_name"])
#         state = creation_object.reboot_vm(conn_create, server_name=data["server_name"])
#         # create_ovs_dpdk_flavor_and_instance()
#         # reboot instance
#         # check ip of instance after vm is turned on
#         delete_object.os_delete_server(conn_delete, server_name=data["server_name"])
#     except:
#         print "Error encountered while executing Test Case: 6 !"
#         print ("\nError: " + str(sys.exc_info()[0]))
#         print ("Cause: " + str(sys.exc_info()[1]))
#         print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
#         delete_object.os_delete_server(conn_delete, server_name=data["server_name"])


# def test_case_8(max_iteration, server_name, flavor_name, disk_size):
#     print("===================================================================================")
#     print("Executing Test Case 8 (Verify instance creation when hugepage free is zero or close\n"
#           "\n to zero but nova cpus are still available)")
#     print("===================================================================================")
#     flavor_munch = creation_object.os_flavor_creation(conn_create, name=flavor_name, ram=22, vcpus=2,
#                                        disk=disk_size)
#     for i in range(0, max_iteration):
#         server_name = server_name+"no%s"%(i)
#         print "Creating instance: %sno%s with %s flavor" %(server_name, i, flavor_name)
#         server = creation_object.os_server_creation(conn_create, server_name, flavor_name=flavor_name,
#                                         image_name=data["static_image"], network_name=data["static_network"],
#                                                 secgroup_name=data["static_secgroup"], availability_zone=data["zone"])
#         print "Created."
#
#     for i in range(0, max_iteration):
#         server_name = server_name+"no%s"%(i)
#         print "Deleting: %sno%s" %(server_name)
#         server = creation_object.os_delete_server(conn_delete, server_name)
#         print ""

def test_case_9():
    logger.info("\n=======================================================================================================")
    logger.info("Executing Test Case 9 (Verify 8 vcpus will be allocated for host os ie 2 sibling pair from each socket)")
    logger.info("=======================================================================================================")
    try:
        command = "sudo taskset -cp 1"
        logger.info ("Trying to execute command: %s"%command)
        for node in cmpt:
            logger.info ("On Compute Node %s IP:%s" %(node, cmpt[node]))
            ssh_obj.ssh_to(logger, cmpt[node], "heat-admin")
            output = ssh_obj.execute_command_return_output(logger, command)
            logger.info (output)
            ssh_obj.ssh_close()
        logger.info ("Need to add the test case pass fail criteria!!!")

    except:
        logger.info ("\nError encountered while executing Test Case: 9 !")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


def test_case_10():
    logger.info("\n==================================================================================================")
    logger.info("Executing Test Case 10 (Check the pmd cores present are distributed according to the specfication)")
    logger.info("==================================================================================================")
    try:
        command1 = "sudo cat /etc/default/grub isolcpus"
        command2 = "sudo ovs-appctl dpif-netdev/pmd-rxq-show"
        ssh_obj.ssh_to(logger, cmpt[0], username_of_nodes)
        logger.info ("Trying to execute command: %s on Compute IP:%s" % (command1, cmpt[0]))
        output1 = ssh_obj.execute_command_return_output(logger, command1)
        logger.info (output1)
        logger.info ("\nTrying to execute command: %s on Compute IP:%s" % (command2, cmpt[0]))
        output2 = ssh_obj.execute_command_return_output(logger, command2)
        logger.info (output2)
        logger.info ("\nNeed to add the test case pass fail criteria!!!")
        ssh_obj.ssh_close()
    except:
        logger.info ("\nError encountered while executing Test Case: 10 !")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


def test_case_11():
    logger.info("\n==========================================================================================")
    logger.info("Executing Test Case 10 (Validates that LACP bonding is working correctly after deployment)")
    logger.info("==========================================================================================")
    try:
        command1 = "sudo cat /etc/default/grub isolcpus"
        command2 = "sudo ovs-appctl dpif-netdev/pmd-rxq-show"
        ssh_obj.ssh_to(logger, cmpt[0], username_of_nodes)
        logger.info ("Trying to execute command: %s on Compute IP:%s" % (command1, cmpt[0]))
        output1 = ssh_obj.execute_command_return_output(logger, command1)
        logger.info (output1)
        logger.info ("\nTrying to execute command: %s on Compute IP:%s" % (command2, cmpt[0]))
        output2 = ssh_obj.execute_command_return_output(logger, command2)
        logger.info (output2)
        logger.info ("\nNeed to add the test case pass fail criteria!!!")
        ssh_obj.ssh_close()
    except:
        logger.info ("\nError encountered while executing Test Case: 11 !")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


def test_case_13_diff_comp_same_net(flavor_name=data["ovsdpdk_flavor"]):
    logger.info("\n=============================================================================")
    logger.info("Executing Test Case 13 (Test the network bandwidth between OVS DPDK instances")
    logger.info ("   On Different Compute and Same Tenant Network)")
    logger.info("=============================================================================")
    try:
        bandwidth1 = iperf3.create_2_instances_on_diff_compute_same_network_and_exec_iperf3(logger, flavor_name=flavor_name)
        # bandwidth2 = iperf3.create_2_instances_on_same_compute_same_network_and_exec_iperf3(flavor_name=data["ovsdpk_flavor"])
        logger.info ("\nNeed to add the test case pass fail criteria!!!")
    except:
        logger.info ("\nError encountered while executing Test Case: 13 \n(On Different Compute and Same Tenant Network)!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case_13_same_comp_same_net(flavor_name=data["ovsdpdk_flavor"]):
    logger.info("\n=============================================================================")
    logger.info("Executing Test Case 13 (Test the network bandwidth between OVS DPDK instances")
    logger.info ("   On Same Compute and Same Tenant Network)")
    logger.info("=============================================================================")
    try:
        bandwidth1 = iperf3.create_2_instances_on_same_compute_same_network_and_exec_iperf3(logger, flavor_name=flavor_name)
        # bandwidth2 = iperf3.create_2_instances_on_same_compute_same_network_and_exec_iperf3(flavor_name=flavor_name)
        logger.info ("\nNeed to add the test case pass fail criteria!!!")
    except:
        logger.info ("Error encountered while executing Test Case: 13\n (On Same Compute and Same Tenant Network)!")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case_14(packet_size_list=[89,512,1470], flavor_name=data["ovsdpdk_flavor"]):
    logger.info("\n================================================================================")
    logger.info("Executing Test Case 14 (Test the network traffic with packet size 89,512 & 1500)")
    logger.info("================================================================================")
    try:
        bandwidth_dict = iperf3.create_2_instances_on_diff_compute_same_network_and_exec_iperf3(logger, flavor_name=flavor_name,
                                                                                    packet_size_list=packet_size_list)
        logger.info ("\nResults")
        for bw in bandwidth_dict:
            logger.info ("Bandwidth =%s (For packet size:%s)" %(bandwidth_dict[bw], bw))
        logger.info ("\n")
    except:
        logger.info ("\nError encountered while executing Test Case: 14!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case_15():
    logger.info("\n==================================================================")
    logger.info("Executing Test Case 15 (Test the network traffic with UDP packets)")
    logger.info("==================================================================")
    try:
        bandwidth = iperf3.create_2_instances_on_same_compute_diff_network_and_exec_iperf3(logger, udp_flag=True,
                                                    flavor_name=data["ovsdpdk_flavor"])

        """ # ping through namespace
        namespace_id = creation_object.get_network_namespace_id(conn_create, network_name)
        ssh_obj.ssh_to(cntl_dict[0], username_of_nodes)
        key_file_name = data["key_file_path"].split("/")[3]
        destination_path = "/home/%s/%s" % (username_of_nodes, key_file_name)
        ssh_obj.send_key_if_not_present(destination_path)
        time.sleep(22)
        output = ssh_obj.ping_check_from_namespace(namespace_id, ip_of_instance1=server1_ip, username_of_instance=image_name,
                                    key_file_path_of_node=destination_path, ip_of_instance2=server2_ip, packet_size=None)
        """
        ## testing things
        ##how to merge repos
    except:
        logger.info ("\nError encountered while executing Test Case: 15!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


def test_case_16():
    logger.info("\n===================================================================")
    logger.info("Executing Test Case 16 (Verify OVS DPDK instance cannot communicate\n"
          " with non OVS DPDK instance created on same tenant network)")
    logger.info("===================================================================")
    try:
        image_name = data["static_image"]
        dpdk_server_mnch = creation_object.os_server_creation(logger, conn_create, server_name="dpdk_server",
                                                              flavor_name=data["ovsdpdk_flavor"],
                                                              image_name=image_name,
                                                              network_name=data["static_network"],
                                                              secgroup_name=data["static_secgroup"],
                                                              availability_zone=data["zone2"])
        server_mnch = creation_object.os_server_creation(logger, conn_create, server_name="server2",
                                                         flavor_name=data["static_flavor"],
                                                         image_name=image_name,
                                                         network_name=data["static_network"],
                                                         secgroup_name=data["static_secgroup"],
                                                         availability_zone=data["zone2"])
        dpdk_server_pri_ip = str(dpdk_server_mnch.accessIPv4)
        s_server_pri_ip = str(server_mnch.accessIPv4)
        out = initialize_ping_check_from_namespace(ips_list=[dpdk_server_pri_ip, s_server_pri_ip],
                               network_name=data["static_network"], image_name=data["static_image"], ping_check=True)
        if out is False:
            logger.info ("\nTest Case 16 Passed, as the communication is unsuccessful.\n")
        else:
            logger.info ("\nTest Case 16 Failed, as the communication is successful.\n")
        delete_object.os_delete_server(logger, conn_delete, "dpdk_server")
        delete_object.os_delete_server(logger, conn_delete, "server2")
    except:
        logger.info ("\nError encountered while executing Test Case: 16!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.os_delete_server(logger, conn_delete, "server1")
        delete_object.os_delete_server(logger, conn_delete, "server2")


def test_case_17(delete_after_create=True):
    logger.info("\n======================================================================")
    logger.info("Executing Test Case 17 (Verify OVS DPDK instances created on different\n"
          " tenant networks but connected to same router can ping each other")
    logger.info("======================================================================")
    try:
        ips_list = creation_object.create_2_instances_on_dif_compute_dif_network(logger, conn_create, server1_name=data["server1_name"],
                                                     server2_name=data["server2_name"], network1_name=data["network1_name"],
                                                     network2_name=data["network2_name"], subnet1_name=data["subnet1_name"],
                                                     subnet2_name=data["subnet2_name"], router_name=data["router_name"],
                                                     port1_name=data["port1_name"], port2_name=data["port2_name"],
                                                     zone1=data["zone2"], zone2=data["zone2"], cidr1=data["cidr1"],
                                                     gateway_ip1=data["gateway_ip1"], cidr2=data["cidr2"],
                                                     gateway_ip2=data["gateway_ip2"], flavor_name=data["static_flavor"],
                                                     image_name=data["static_image"],secgroup_name=data["static_secgroup"],
                                                     assign_floating_ip=False)
        out = initialize_ping_check_from_namespace(ips_list,
                               network_name=data["network1_name"], image_name=data["static_image"], ping_check=True)
        if out is True:
            logger.info ("\nTest Case 17 Passed, Ping successful.\n")
        else:
            logger.info ("\nTest Case 17 Failed, Ping unsuccessful.\n")
        if delete_after_create == True:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=data["server1_name"],
                                                                        server2_name=data["server2_name"],
                                                                        network1_name=data["network1_name"],
                                                                        network2_name=data["network2_name"],
                                                                        router_name=data["router_name"],
                                                                        port1_name=data["port1_name"],
                                                                        port2_name=data["port2_name"])
        else:
            logger.info ("\nNote: Both instances: %s and %s are not deleted!\n" % (data["server1_name"],data["server2_name"]))
    except:
        logger.info ("\nError encountered while executing Test Case: 17!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=data["server1_name"],
                                                                    server2_name=data["server2_name"],
                                                                    network1_name=data["network1_name"],
                                                                    network2_name=data["network2_name"],
                                                                    router_name=data["router_name"],
                                                                    port1_name=data["port1_name"],
                                                                    port2_name=data["port2_name"])


def test_case_23():
    logger.info("\n================================================================")
    logger.info("Executing Test Case 23 (Validate vcpus pinned to host OS, to pmd\n"
          " physical, to pmd virtual and for instances.")
    logger.info("================================================================")
    try:
        for node in cmpt:
            logger.info ("Checking on Compute Node%s.." % node)
            ssh_obj.ssh_to(logger, cmpt[node], username_of_nodes)
            output1 = ssh_obj.execute_command_return_output(logger, "sudo cat /root/parameters.ini")
            logger.info (output1)
            output2 = ssh_obj.execute_command_return_output(logger, "sudo ovs-appctl dpif-netdev/pmd-rxq-show")
            logger.info (output2)
            ssh_obj.ssh_close()
    except:
        logger.info ("\nError encountered while executing Test Case: 17!")
        logger.info ("Error: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()


# pdb.set_trace()

#test_case_3(data["ovsdpdk_flavor"], data["zone1"], data["static_image"], data["port_name"], data["server_name"], data["static_secgroup"], data["static_network"], data["static_router"], data["subnet_name"], data["cidr"], data["gateway_ip"], deleteall=True)

#test_case_4(data["ovsdpdk_flavor"], data["zone1"], data["static_image"], data["port_name"], data["server_name"], data["static_secgroup"], data["static_network"], data["static_router"], data["subnet_name"], data["cidr"], data["gateway_ip"], cmpt[0], cmpt[1], cmpt[2], deleteall=True)
#test_case_5(data["ovsdpdk_flavor"], data["zone1"], data["static_image"], data["port_name"], data["server_name"], data["static_secgroup"], data["static_network"], data["static_router"], data["subnet_name"], data["cidr"], data["gateway_ip"], cmpt[0], cmpt[1], cmpt[2], deleteall=True)

# test_case_9()
# test_case_10()
# test_case_11()
# test_case_13_diff_comp_same_net()
# test_case_13_same_comp_same_net()
# test_case_14()
test_case_15()
# test_case_16()
# test_case_17()
# test_case_23()
