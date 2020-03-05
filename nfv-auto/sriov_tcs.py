import commands
import os
import json
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import pdb
import sys
import time
#########################logger code start
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
from source_R8rc import Source_Module

feature_name = "SRIOV"

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
#########################logger code end
feature_setup_file = "sriov-setup.json"

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


if os.path.exists(feature_setup_file):
    f_data = None
    try:
        with open(feature_setup_file) as data_file:
            f_data = json.load(data_file)
        f_data = {str(i): str(j) for i, j in f_data.items()}
    except:
        logger.info ("\nFAILURE!!! error in %s file!" % feature_setup_file)
else:
    logger.info ("\nFAILURE!!! %s file not found!!!\nUnable to execute sriov script.\n\n" % feature_setup_file)
    exit()


def ssh_to_instance1_and_ping_instance2(username_of_instance1, ip_of_instance1, ip_of_instance2):
    ssh_obj.ssh_to(logger, ip=ip_of_instance1, username=username_of_instance1, key_file_name=data["key_file_path"])
    logger.info ("Pinging %s from %s" % (ip_of_instance2, ip_of_instance1))
    result = ssh_obj.simple_ping_check(logger, ip_of_instance2)
    if result == True:
        logger.info ("---Ping Successful!")
    else:
        logger.info ("---Ping Unsuccessful!")
    ssh_obj.ssh_close()
    return result

def get_sriov_interface_names_from_ini_file():
    ssh_obj.ssh_to(logger, ip=sah_node_ip, username=sah_node_username, password=sah_node_password)
    data = ssh_obj.read_remote_file(csp_profile_ini_file_path)
    interface_names = []
    for line in data.split("\n"):
        if "ComputeSriovInterface" in line:
            if "#" in line:
                pass
            else:
                logger.info (line)
                interface_names.append(line.split("=")[1])
    ssh_obj.ssh_close()
    logger.info (interface_names)
    return interface_names


def get_legacy_interface_names_from_ini_file():
    ssh_obj.ssh_to(logger, ip=sah_node_ip, username=sah_node_username, password=sah_node_password)
    data = ssh_obj.read_remote_file(csp_profile_ini_file_path)
    interface_names = []
    for line in data.split("\n"):
        if "ComputeOvsDpdkInterface" in line:
            if "#" in line:
                pass
            else:
                logger.info (line)
                interface_names.append(line.split("=")[1])
    ssh_obj.ssh_close()
    logger.info (interface_names)
    return interface_names

def check_number_of_vfs(zone):
    if zone == data["zone1"]:
        ip = cmpt[0]
    elif zone == data["zone2"]:
        ip = cmpt[1]
    elif zone == data["zone3"]:
        ip = cmpt[2]
    ini_file_interface_names = get_sriov_interface_names_from_ini_file()
    ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)
    interfaces_list = ssh_obj.check_interface_names(logger)
    for i in range(0,len(ini_file_interface_names)):
        ini_file_interface_names[i] = ini_file_interface_names[i] + "_"
    logger.info (ini_file_interface_names)
    # pdb.set_trace()
    result = []
    for interface in interfaces_list:
        for i in ini_file_interface_names:
            if i in interface:
                result.append(interface)
                logger.info (interface)
    logger.info (result)
    vf_count = len(result)
    logger.info (vf_count)
    ssh_obj.ssh_close()
    return vf_count

test_case = {
    6: "Create two sriov-enabled instance on same compute node and verify the communication",
    7: "Create two sriov-enabled instance on different compute node and verify the communication",
    8: "Create one sriov-enabled and one simple instance on same compute node\n and verify the communication",
    9: "Create one sriov-enabled and one simple instance on different compute\n node and verify the communication",
    11: "Create one sriov-enabled and one simple instance on different compute\n node and different networks. Verify the communication ",
    12: "Create one sriov-enabled and one simple instance on same compute node\n different networks. verify the communication",
    13: "Create two sriov-enabled instances on same compute node and different\n networks. verify the communication",
    14: "Create two sriov-enabled instances on different compute node and\n different networks. verify the communication",
    # 15: "Create four SRIOV enable instances in a compute node and populate them\n through iperf3 with eachother",
    # 16: "Create eight SRIOV enable instances four per compute node and populate\n them through iperf3 with eachother",
    3: "Create SRIOV enabled instance",
    4: "ssh to sriov-enabled instance",
    5: "Verify the VFs creations on compute node"
    # 10: "Executing Test Case 10 (Reboot the instance, after the instance is up,\n check the VF connectivity.)"
}


# def test_case_3():
#     logger.info "Test Case 3: %s" %(rest[3])
#     # Aggregate Parameters
#     agr_name = "sriov1"
#     availability_zone = "sriov2"
#     host_name = "overcloud-compute-0.localdomain"
#     # Flavor Parameters
#     flavor_name = "m1.medium_2cpu"
#     ram = 4096
#     vcpus = 2
#     disk = 150
#     # Network Parameters
#     network_name = "sriov_net"
#     provider_dict = {'network_type': 'vlan', 'physical_network': 'sriov1'}
#     # Subnet Parameters
#     cidr = "10.0.10.0/24"
#     subnet_name = "sriov_sub"
#     dhcp_boolean = True
#     allocation_pools_list_dict = [
#                                     {
#                                         "start": "192.168.10.20",
#                                         "end": "192.168.10.50"
#                                     }
#                                  ]
#     gateway_ip = ""
#     # Port Parameters
#     port_name = "sriov_p1"
#     vnic_type = "direct"
#     fixed_ips_list_dict =[
#                             {
#                                 "ip_address": "23.23.23.1",
#                                 "mac_address": "fa:16:3e:c4:cd:3f"
#                             }
#                          ]
#     # Server Parameters
#     server_name = "sriov_vm"
#     nic_list = ["port-id=%s" % port.id]
#     aggr = creation_object.os_aggregate_creation_and_add_host(logger, conn_create, agr_name, availability_zone, host_name)
#     flavor = creation_object.os_flavor_creation(logger, conn_create, flavor_name, ram, vcpus, disk)
#     network, port = creation_object.os_network_creation_with_network_provider(logger, conn_create, network_name,
#                                                                               provider_dict, cidr, dhcp_boolean,
#                                                                               allocation_pools_list_dict, subnet_name,
#                                                                               gateway_ip, port_name, vnic_type,
#                                                                               fixed_ips_list_dict)
#     server = creation_object.os_server_creation_for_sriov(server_name, flavor_name,
#                 image_name, availability_zone, nic_list)
#     return server_name


def test_case_1(network_name=f_data["sriov_network_name"],
                port_name=f_data["sriov_port"],
                router_name=f_data["sriov_router"],
                subnet_name=f_data["sriov_subnetwork"],
                cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=True, subnet_bool=True, port_bool=True,
                flavor_name=f_data["sriov_flavor"], availability_zone=f_data["zone1"],
                image_name=f_data["static_image"],server_name=f_data["sriov_server"],
                security_group_name=f_data["static_secgroup"],key_name=f_data["key_name"],
deleteall=False
                ):
    """STEPS FOR CREATION OF SRIOV ENABLED INSTANCE
        1. Create a zone named sriov
        2. Create aggregate and add host sriov
        3. Create flavor with 4GB ram, 150GB disk, 2 vcpu
        4. Create a Network named sriov_net
        5. Create Subnet named sriov_sub
        6. Create port with vnic type = direct named it as sriov_port
        7. Create VM using above created nic port"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 1:     Create SRIOV Enabled Instance.                                     =====")
    logger.info("==========================================================================================================")
    try:
        # agg = creation_object.os_aggregate_creation_and_add_host(logger, conn_create, name, availablity_zone, host_name)
        # fal = creation_object.os_flavor_creation(logger, conn_create, "sriov_flavor", 4096, 2, 150)
        # [network_id, subnet_id, port_id, port_ip]
        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
        #                                                           network_name=network_name,
        #                                                           router_name=router_name, port_name=port_name)
        # exit()
        for x in range(1,8):
            port_name="s_port%s"%x
            server_name="s_instance%s"%x
            if x > 1:
                network_bool="False"
                subnet_bool="False"
            output = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                      port_name=port_name,
                                                                      router_name=router_name,
                                                                      subnet_name=subnet_name,
                                                                      cidr=cidr,
                                                                      gateway=gateway,
                                             network_bool=network_bool, subnet_bool=subnet_bool, port_bool=port_bool,
                                             flavor_name=flavor_name,
                                             availability_zone=availability_zone,
                                             image_name=image_name,
                                             server_name=server_name,
                                             security_group_name=security_group_name,
                                             key_name=key_name)
            # pdb.set_trace()
            time.sleep(50)
            ping = ssh_obj.locally_ping_check(logger, ip=output[2][1])
            if ping:
                logger.info ("Test 1 SUCCESSFUL")
            else:
                logger.info ("Test 1 FAILED")
            if deleteall:
                delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                          network_name=network_name,
                                                            router_name=router_name, port_name=port_name)
            else:
                logger.info ("Note: Nothing is deleted!")
        return output
    except:
        logger.info ("Unable to execute test case 1")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)


def test_case_2(network_name=f_data["sriov_network_name"],
                port_name=f_data["sriov_port"],
                router_name=f_data["sriov_router"],
                subnet_name=f_data["sriov_subnetwork"],
                cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=True, subnet_bool=True, port_bool=True,
                flavor_name=f_data["sriov_flavor"], availability_zone=f_data["zone"],
                image_name=f_data["static_image"],server_name=f_data["sriov_server"],
                security_group_name=f_data["static_secgroup"],key_name=f_data["key_name"],
deleteall=True
                ):
    """STEPS FOR CREATION OF SRIOV ENABLED INSTANCE
        1. Create a zone named sriov
        2. Create aggregate and add host sriov
        3. Create flavor with 4GB ram, 150GB disk, 2 vcpu
        4. Create a Network named sriov_net
        5. Create Subnet named sriov_sub
        6. Create port with vnic type = direct named it as sriov_port
        7. Create VM using above created nic port"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 2:     SSH SRIOV Enabled Instance.                                            =====")
    logger.info("==========================================================================================================")
    try:
        # agg = creation_object.os_aggregate_creation_and_add_host(logger, conn_create, name, availablity_zone, host_name)
        # fal = creation_object.os_flavor_creation(logger, conn_create, "sriov_flavor", 4096, 2, 150)
        # [network_id, subnet_id, port_id, port_ip]
        output = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                  port_name=port_name,
                                                                  router_name=router_name,
                                                                  subnet_name=subnet_name,
                                                                  cidr=cidr,
                                                                  gateway=gateway,
                                         network_bool=network_bool, subnet_bool=subnet_bool, port_bool=port_bool,
                                         flavor_name=flavor_name,
                                         availability_zone=availability_zone,
                                         image_name=image_name,
                                         server_name=server_name,
                                         security_group_name=security_group_name,
                                         key_name=key_name)
        # pdb.set_trace()
        time.sleep(50)
        ssh_obj.ssh_to(logger, ip=output[2][1], username="centos", key_file_name=data["key_file_path"])
        ip = ssh_obj.execute_command_return_output(logger, "sudo ip a")
        ssh_obj.ssh_close()
        if output[2][0] in ip:
            logger.info ("Test 2 SUCCESSFUL")
        else:
            logger.info ("Test 2 FAILED")
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                      network_name=network_name,
                                                        router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")
        return output
    except:
        logger.info ("Unable to execute test case 2")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)





def test_case_3(network_name=f_data["sriov_network_name"],
                port_name=f_data["sriov_port"],
                router_name=f_data["sriov_router"],
                subnet_name=f_data["sriov_subnetwork"],
                cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=True, subnet_bool=True, port_bool=True,
                flavor_name=f_data["sriov_flavor"], availability_zone=f_data["zone"],
                image_name=f_data["static_image"],server_name=f_data["sriov_server"],
                security_group_name=f_data["static_secgroup"],key_name=f_data["key_name"]
                ):
    """Step 1.  After creating the sriov-enabled instance, ssh to compute node where instance is resides on
        Step 2. Run the ifconfig command to verify the creation of VFs of ports assigned in settings file"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 3:     Verify the VFs creations on compute node.                          =====")
    logger.info("==========================================================================================================")
    try:
        vfcount_before_server_creation = check_number_of_vfs(zone=availability_zone)
        output = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                  port_name=port_name,
                                                                  router_name=router_name,
                                                                  subnet_name=subnet_name,
                                                                  cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=network_bool, subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=flavor_name,
                                                                  availability_zone=availability_zone,
                                                                  image_name=image_name,
                                                                  server_name=server_name,
                                                                  security_group_name=security_group_name,
                                                                  key_name=key_name)
        vfcount_after_server_creation = check_number_of_vfs(zone=availability_zone)
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)
        vfcount_after_server_deletion = check_number_of_vfs(zone=availability_zone)
        if vfcount_after_server_deletion > vfcount_after_server_creation and vfcount_before_server_creation > vfcount_after_server_creation and vfcount_after_server_deletion == vfcount_before_server_creation:
            logger.info ("Total number of VF's %s" %vfcount_before_server_creation)
            logger.info ("1 VF is consumed when instance created....%s" %vfcount_after_server_creation)
            logger.info ("1 VF is returned when instance deleted....%s" %vfcount_after_server_deletion)
            logger.info ("Test Successful")
        else:
            logger.info ("server creation failed / server is not created on the given compute")
            logger.info ("Test Failed")
    except:
        logger.info ("Unable to execute test case 3")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)


def test_case4(server1_name=f_data["sriov_server1"], server2_name=f_data["sriov_server2"],
               network_name=f_data["sriov_network_name"],
               subnet_name=f_data["sriov_subnetwork"],
               router_name=f_data["sriov_router"],
               port1_name=f_data["sriov_port1"], port2_name=f_data["sriov_port2"],
               zone=f_data["zone"],
               cidr=f_data["cidr"], gateway_ip=f_data["gateway"],
               flavor_name=f_data["sriov_flavor"],
               image_name=f_data["static_image"],
               secgroup_name=f_data["static_secgroup"],
               key_name=f_data["key_name"],
               deleteall=True):

    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 4:     Creating Same Compute and network sriov Instances.                =====")
    logger.info("==========================================================================================================")
    """1. Create instance-1 and instance-2 on same network and compute node e.g compute0
        2. ssh to instance-1
         3. ping to instance-2's ip"""
    # delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
    #                                                                          server2_name=server2_name,
    #                                                                          network_name=network_name,
    #                                                                          router_name=router_name,
    #                                                                          port1_name=port1_name,
    #                                                                          port2_name=port2_name)
    try:
        output = creation_object.create_2_instances_sriov_enabled_on_same_compute_same_network(logger, conn_create,
                                                    server1_name=server1_name, server2_name=server2_name,
                                                    network_name=network_name, subnet_name=subnet_name,
                                                    router_name=router_name, port1_name=port1_name,
                                                    port2_name=port2_name, zone=zone, cidr=cidr,
                                                    gateway_ip=gateway_ip, flavor_name=flavor_name, image_name=image_name,
                                                    secgroup_name=secgroup_name, key_name=key_name,
                                                    assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 1 to Sriov Instance 2")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[0][2][1],
                                                   ip_of_instance2=output[1][2][0])
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 2 to Sriov Instance 1")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[1][2][1],
                                                   ip_of_instance2=output[0][2][0])
        # ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[0][2][1], ip_of_instance2=output[1][2][0])

        if ping==1:
            logger.info ("Test 4 SUCCESSFUL")
        else:
            logger.info ("Test 4 failed")

        ssh_obj.ssh_close()

        if deleteall:
            delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                       server2_name=server2_name,
                                                                       network_name=network_name,
                                                                       router_name=router_name,
                                                                       port1_name=port1_name,
                                                                       port2_name=port2_name)
        return ping
    except:
        logger.info ("Unable to execute test case 4")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                   server2_name=server2_name,
                                                                   network_name=network_name,
                                                                   router_name=router_name,
                                                                   port1_name=port1_name,
                                                                   port2_name=port2_name)



def test_case5(server1_name=f_data["sriov_server1"], server2_name=f_data["sriov_server2"],
               network_name=f_data["sriov_network_name"],
               subnet_name=f_data["sriov_subnetwork"],
               router_name=f_data["sriov_router"],
               port1_name=f_data["sriov_port1"], port2_name=f_data["sriov_port2"],
               zone1=f_data["zone"],zone2=f_data["zone1"],
               cidr=f_data["cidr"], gateway_ip=f_data["gateway"],
               flavor_name=f_data["sriov_flavor"],
               image_name=f_data["static_image"],
               secgroup_name=f_data["static_secgroup"],
               key_name=f_data["key_name"],
               deleteall=True):

    """1. Create instance-1 and instance-2 on same network and different compute nodes e.g instance-1 on compute0 and instance-2 on compute1
        2. ssh to instance-1
         3. ping to instance-2's ip"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 5:     Creating Different Compute and Same Network sriov Instances.           =====")
    logger.info("==========================================================================================================")
    try:
        output = creation_object.create_2_instances_sriov_enabled_on_diff_compute_same_network(logger, conn_create,
                                                    server1_name=server1_name, server2_name=server2_name,
                                                    network_name=network_name, subnet_name=subnet_name,
                                                    router_name=router_name, port1_name=port1_name,
                                                    port2_name=port2_name, zone1=zone1, zone2=zone2, cidr=cidr,
                                                    gateway_ip=gateway_ip, flavor_name=flavor_name, image_name=image_name,
                                                    secgroup_name=secgroup_name, key_name=key_name,
                                                    assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 1 to Sriov Instance 2")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[0][2][1],
                                                   ip_of_instance2=output[1][2][0])
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 2 to Sriov Instance 1")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[1][2][1],
                                                   ip_of_instance2=output[0][2][0])
        # ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=output[0][2][1], ip_of_instance2=output[1][2][0])

        if ping==1:
            logger.info ("Test 5 SUCCESSFUL")
        else:
            logger.info ("Test 5 failed")

        ssh_obj.ssh_close()

        if deleteall:
            delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                       server2_name=server2_name,
                                                                       network_name=network_name,
                                                                       router_name=router_name,
                                                                       port1_name=port1_name,
                                                                       port2_name=port2_name)
        return ping
    except:
        logger.info ("Unable to execute test case 5")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                   server2_name=server2_name,
                                                                   network_name=network_name,
                                                                   router_name=router_name,
                                                                   port1_name=port1_name,
                                                                   port2_name=port2_name)


def test_case6( network_name=f_data["network_name"],
                sriov_port=f_data["sriov_port"],
                legacy_port=f_data["legacy_port"],
                subnet_name=f_data["subnet_name"], cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=False, subnet_bool=False, port_bool=False,
                router_name=f_data["router_name"],
                zone=f_data["zone"],
                sriov_flavor=f_data["sriov_flavor"], legacy_flavor=f_data["legacy_flavor"],
                sriov_server=f_data["sriov_server"], legacy_server=f_data["legacy_server"],
                image_name=f_data["static_image"],
                key_name=data["key_name"],
                secgroup=data["static_secgroup"],
deleteall=True
):
    """1.Create sriov and legacy instances on same compute and on same network.
        2.Create sriov and legacy instances on different compute and on same network
         3.Create sriov and legacy instances on same compute and different network
          4.Create sriov and legacy instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 6:     Ping an sriov instance to legacy instance in different scenarios             ====")
    logger.info("====  .same compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=legacy_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=legacy_port)
    #1.Create sriov and ovslegacy instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=legacy_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=legacy_port)

    try:
        network = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=network_name,
                                                                        port_name=sriov_port,
                                        subnet_name=subnet_name, cidr=cidr, gateway=gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        # pdb.set_trace()
        router = creation_object.os_router_creation(logger, conn_create, router_name=router_name,
                                                     port_name=sriov_port, net_name=network_name)
        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=subnet_name,
                                                                  cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        legacy = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=legacy_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name, port_name=legacy_port,
                                                                               zone=zone, cidr=cidr,
                                                            gateway_ip=gateway, flavor_name=legacy_flavor, image_name=image_name,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("==============================================")
        logger.info("Pinging from Sriov Instance to Legacy Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov[2][1],
                                                   ip_of_instance2=legacy[3])
        logger.info("==============================================")
        logger.info("Pinging from Legacy Instance to Sriov Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=legacy[4],
                                                   ip_of_instance2=sriov[2][0])

        if ping:
            logger.info ("Test 6 same compute and same network successful")
        else:
            logger.info ("Test 6 same compute and same network failed")

        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                             server2_name=legacy_server,
                                                                             network_name=network_name,
                                                                             router_name=router_name,
                                                                             port1_name=sriov_port,
                                                                             port2_name=legacy_port)
        return ping
    except:
        logger.info ("Unable to execute test case 6")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                                 server2_name=legacy_server,
                                                                                 network_name=network_name,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port,
                                                                                 port2_name=legacy_port)


def test_case7(network_name = f_data["network_name"],
    sriov_port = f_data["sriov_port"],
    legacy_port = f_data["legacy_port"],
    subnet_name = f_data["subnet_name"], cidr = f_data["cidr"], gateway = f_data["gateway"],
    network_bool = False, subnet_bool = False, port_bool = False,
    router_name = f_data["router_name"],
    zone1 = f_data["zone"], zone2 = f_data["zone1"], image_name = f_data["static_image"],
    sriov_flavor = f_data["sriov_flavor"], legacy_flavor = f_data["legacy_flavor"],
    sriov_server = f_data["sriov_server"], legacy_server = f_data["legacy_server"],
    key_name = data["key_name"],
    secgroup = data["static_secgroup"],
deleteall=True
):

    """1.Create sriov and legacy instances on same compute and on same network.
        2.Create sriov and legacy instances on different compute and on same network
         3.Create sriov and legacy instances on same compute and different network
          4.Create sriov and legacy instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 7:     Ping an sriov instance to legacy instance in different scenarios            ====")
    logger.info("====  .diff compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=legacy_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=legacy_port)
    # exit()
    #1.Create sriov and legacy instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=legacy_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=legacy_port)
    try:
        network = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=network_name,
                                                                        port_name=sriov_port,
                                        subnet_name=subnet_name, cidr=cidr, gateway=gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        # pdb.set_trace()
        router = creation_object.os_router_creation(logger, conn_create, router_name=router_name,
                                                     port_name=sriov_port, net_name=network_name)
        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=subnet_name,
                                                                  cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone1,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        legacy = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=legacy_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name, port_name=legacy_port,
                                                                               zone=zone2, cidr=cidr,
                                                            gateway_ip=gateway, flavor_name=legacy_flavor, image_name=image_name,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        # pdb.set_trace()
        time.sleep(50)
        logger.info("==============================================")
        logger.info("Pinging from Sriov Instance to Legacy Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov[2][1],
                                                   ip_of_instance2=legacy[3])
        logger.info("==============================================")
        logger.info("Pinging from Legacy Instance to Sriov Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=legacy[4],
                                                   ip_of_instance2=sriov[2][0])

        if ping:
            logger.info ("Test 7 diff compute and same network successful")
        else:
            logger.info ("Test 7 diff compute and same network failed")

        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                             server2_name=legacy_server,
                                                                             network_name=network_name,
                                                                             router_name=router_name,
                                                                             port1_name=sriov_port,
                                                                             port2_name=legacy_port)
        return ping
    except:
        logger.info ("Unable to execute test case 7")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                                 server2_name=legacy_server,
                                                                                 network_name=network_name,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port,
                                                                                 port2_name=legacy_port)


def test_case8( sriov_network=f_data["sriov_network"], legacy_network=f_data["legacy_network"],
                sriov_port= f_data["sriov_port"], legacy_port=f_data["legacy_port"],
                sriov_subnet=f_data["sriov_subnet"], legacy_subnet=f_data["legacy_subnet"],
                sriov_cidr=f_data["sriov_cidr"], sriov_gateway=f_data["sriov_gateway"],
                legacy_cidr=f_data["legacy_cidr"], legacy_gateway=f_data["legacy_gateway"],
                network_bool=False, subnet_bool=False, port_bool=False,
                router_name=f_data["router_name"],
                zone=f_data["zone2"],
                image_name=f_data["static_image"],
                sriov_flavor = f_data["sriov_flavor"], legacy_flavor = f_data["legacy_flavor"],
                sriov_server = f_data["sriov_server"], legacy_server = f_data["legacy_server"],
                key_name = data["key_name"],
                secgroup = data["static_secgroup"],
    deleteall=True
            ):
    """1.Create sriov and ovslegacy instances on same compute and on same network.
        2.Create sriov and ovslegacy instances on different compute and on same network
         3.Create sriov and ovslegacy instances on same compute and different network
          4.Create sriov and ovslegacy instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 8:     Ping an sriov instance to legacy instance in different scenarios             ====")
    logger.info("====  .same compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=legacy_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=legacy_port)
    #1.Create sriov and ovslegacy instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=legacy_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=legacy_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_legacy = creation_object.os_network_creation(logger, conn_create, net_name=legacy_network,
                                                           cidr=legacy_cidr,
                                                           subnet_name=legacy_subnet,
                                                           gatewy=legacy_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=legacy_port,
                                                         net1_name=sriov_network, net2_name=legacy_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        legacy = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=legacy_server,
                                                                               network_name=legacy_network,
                                                                               subnet_name=legacy_subnet,
                                                                               router_name=router_name, port_name=legacy_port,
                                                                               zone=zone, cidr=legacy_cidr,
                                                            gateway_ip=legacy_gateway, flavor_name=legacy_flavor, image_name=image_name,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("==============================================")
        logger.info("Pinging from Sriov Instance to Legacy Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov[2][1],
                                                   ip_of_instance2=legacy[3])
        logger.info("==============================================")
        logger.info("Pinging from Legacy Instance to Sriov Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=legacy[4],
                                                   ip_of_instance2=sriov[2][0])

        if ping:
            logger.info ("Test 8 same compute and diff network successful")
        else:
            logger.info ("Test 8 same compute and diff network failed")

        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=legacy_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=legacy_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=legacy_port)

        return ping
    except:
        logger.info ("Unable to execute test case 8")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=legacy_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=legacy_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=legacy_port)


def test_case9(sriov_network=f_data["sriov_network"], legacy_network=f_data["legacy_network"],
                sriov_port= f_data["sriov_port"], legacy_port=f_data["legacy_port"],
                sriov_subnet=f_data["sriov_subnet"], legacy_subnet=f_data["legacy_subnet"],
                sriov_cidr=f_data["sriov_cidr"], sriov_gateway=f_data["sriov_gateway"],
                legacy_cidr=f_data["legacy_cidr"], legacy_gateway=f_data["legacy_gateway"],
                network_bool=False, subnet_bool=False, port_bool=False,
                router_name=f_data["router_name"],
                zone1=f_data["zone2"], zone2=f_data["zone1"],
                image_name=f_data["static_image"],
                sriov_flavor = f_data["sriov_flavor"], legacy_flavor = f_data["legacy_flavor"],
                sriov_server = f_data["sriov_server"], legacy_server = f_data["legacy_server"],
                key_name = data["key_name"],
                secgroup = data["static_secgroup"],
    deleteall=True
):
    """1.Create sriov and legacy instances on same compute and on same network.
        2.Create sriov and legacy instances on different compute and on same network
         3.Create sriov and legacy instances on same compute and different network
          4.Create sriov and legacy instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 9:     Ping an sriov instance to legacy instance in different scenarios             ====")
    logger.info("====  .diff compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=legacy_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=legacy_port)
    #1.Create sriov and ovslegacy instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=legacy_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=legacy_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_legacy = creation_object.os_network_creation(logger, conn_create, net_name=legacy_network,
                                                           cidr=legacy_cidr,
                                                           subnet_name=legacy_subnet,
                                                           gatewy=legacy_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=legacy_port,
                                                         net1_name=sriov_network, net2_name=legacy_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone1,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        legacy = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=legacy_server,
                                                                               network_name=legacy_network,
                                                                               subnet_name=legacy_subnet,
                                                                               router_name=router_name, port_name=legacy_port,
                                                                               zone=zone2, cidr=legacy_cidr,
                                                                                gateway_ip=legacy_gateway,
                                                                                flavor_name=legacy_flavor, image_name=image_name,
                                                                                secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("==============================================")
        logger.info("Pinging from Sriov Instance to Legacy Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov[2][1],
                                                   ip_of_instance2=legacy[3])
        logger.info("==============================================")
        logger.info("Pinging from Legacy Instance to Sriov Instance")
        logger.info("==============================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=legacy[4],
                                                   ip_of_instance2=sriov[2][0])

        if ping:
            logger.info ("Test 9 diff compute and diff network successful")
        else:
            logger.info ("Test 9 diff compute and diff network failed")

        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=legacy_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=legacy_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=legacy_port)

        return ping
    except:
        logger.info ("Unable to execute test case 9")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=legacy_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=legacy_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=legacy_port)

def test_case10(    sriov_network1=f_data["sriov_network1"],
                    sriov_network2=f_data["sriov_network2"],
                    sriov_port1=f_data["sriov_port1"],
                    sriov_port2=f_data["sriov_port2"],
                    sriov_subnet1=f_data["sriov_subnet1"],
        sriov_subnet2=f_data["sriov_subnet2"],
        sriov_cidr1=f_data["sriov_cidr1"], sriov_gateway1=f_data["sriov_gateway1"],
        sriov_cidr2=f_data["sriov_cidr2"], sriov_gateway2=f_data["sriov_gateway2"],
        network_bool=False, subnet_bool=False, port_bool=False,
        router_name=f_data["sriov_router"], zone=f_data["zone2"],
        image_name=f_data["static_image"],
        sriov_server1=f_data["sriov_server1"],
        sriov_server2=f_data["sriov_server2"],
        key_name=data["key_name"], secgroup=data["static_secgroup"],sriov_flavor = f_data["sriov_flavor"],
deleteall=True
):
    """1.Create sriov and sriov instances on same compute and on same network.
        2.Create sriov and sriov instances on different compute and on same network
         3.Create sriov and sriov instances on same compute and different network
          4.Create sriov and sriov instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 10:     Ping an sriov instance to sriov instance in different scenarios             ====")
    logger.info("====  .same compute diff network ====")
    logger.info("==========================================================================================================")

    try:
        network_sriov1 = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network1,
                                                                        port_name=sriov_port1,
                                        subnet_name=sriov_subnet1, cidr=sriov_cidr1, gateway=sriov_gateway1,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_sriov2 = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network2,
                                                                        port_name=sriov_port2,
                                        subnet_name=sriov_subnet2, cidr=sriov_cidr2, gateway=sriov_gateway2,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2,
                                                         net1_name=sriov_network1, net2_name=sriov_network2)

        sriov1 = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network1,
                                                                  port_name=sriov_port1,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet1,
                                                                  cidr=sriov_cidr1,
                                                                  gateway=sriov_gateway1,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server1,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        sriov2 = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network2,
                                                                  port_name=sriov_port2,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet2,
                                                                  cidr=sriov_cidr2,
                                                                  gateway=sriov_gateway2,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server2,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 1 to Sriov Instance 2")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov1[2][1],
                                                   ip_of_instance2=sriov2[2][0])
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 2 to Sriov Instance 1")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov2[2][1],
                                                   ip_of_instance2=sriov1[2][0])

        if ping:
            logger.info ("Test 10 same compute and diff network successful")
        else:
            logger.info ("Test 10 same compute and diff network failed")

        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                        server2_name=sriov_server2,
                                                                        network1_name=sriov_network1,
                                                          network2_name=sriov_network2,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port1, port2_name=sriov_port2)

        return ping
    except:
        logger.info ("Unable to execute test case 10")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                    server2_name=sriov_server2,
                                                                    network1_name=sriov_network1,
                                                                    network2_name=sriov_network2,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2)


def test_case11(
sriov_network1=f_data["sriov_network1"],
                    sriov_network2=f_data["sriov_network2"],
                    sriov_port1=f_data["sriov_port1"],
                    sriov_port2=f_data["sriov_port2"],
                    sriov_subnet1=f_data["sriov_subnet1"],
        sriov_subnet2=f_data["sriov_subnet2"],
        sriov_cidr1=f_data["sriov_cidr1"], sriov_gateway1=f_data["sriov_gateway1"],
        sriov_cidr2=f_data["sriov_cidr2"], sriov_gateway2=f_data["sriov_gateway2"],
        network_bool=False, subnet_bool=False, port_bool=False,
        router_name=f_data["sriov_router"], zone1=f_data["zone2"],zone2=f_data["zone"],
        image_name=f_data["static_image"],
        sriov_server1=f_data["sriov_server1"],
        sriov_server2=f_data["sriov_server2"],
        key_name=data["key_name"], secgroup=data["static_secgroup"],sriov_flavor = f_data["sriov_flavor"],
deleteall=True
):
    """1.Create sriov and sriov instances on same compute and on same network.
        2.Create sriov and sriov instances on different compute and on same network
         3.Create sriov and sriov instances on same compute and different network
          4.Create sriov and sriov instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 11:     Ping an sriov instance to sriov instance in different scenarios             ====")
    logger.info("====  .diff compute diff network ====")
    logger.info("==========================================================================================================")

    try:
        network_sriov1 = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network1,
                                                                        port_name=sriov_port1,
                                        subnet_name=sriov_subnet1, cidr=sriov_cidr1, gateway=sriov_gateway1,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_sriov2 = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network2,
                                                                        port_name=sriov_port2,
                                        subnet_name=sriov_subnet2, cidr=sriov_cidr2, gateway=sriov_gateway2,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2,
                                                         net1_name=sriov_network1, net2_name=sriov_network2)

        sriov1 = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network1,
                                                                  port_name=sriov_port1,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet1,
                                                                  cidr=sriov_cidr1,
                                                                  gateway=sriov_gateway1,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone1,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server1,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        sriov2 = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network2,
                                                                  port_name=sriov_port2,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet2,
                                                                  cidr=sriov_cidr2,
                                                                  gateway=sriov_gateway2,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone2,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server2,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)
        # pdb.set_trace()
        time.sleep(50)
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 1 to Sriov Instance 2")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov1[2][1],
                                                   ip_of_instance2=sriov2[2][0])
        logger.info("=================================================")
        logger.info("Pinging from Sriov Instance 2 to Sriov Instance 1")
        logger.info("=================================================")
        ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov2[2][1],
                                                   ip_of_instance2=sriov1[2][0])

        if ping:
            logger.info ("Test 11 diff compute and diff network successful")
        else:
            logger.info ("Test 11 diff compute and diff network failed")

        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                        server2_name=sriov_server2,
                                                                        network1_name=sriov_network1,
                                                          network2_name=sriov_network2,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port1, port2_name=sriov_port2)

        return ping
    except:
        logger.info ("Unable to execute test case 11")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                    server2_name=sriov_server2,
                                                                    network1_name=sriov_network1,
                                                                    network2_name=sriov_network2,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2)




# pdb.set_trace()
# test_case_5(zone="sriov")

test_case_1()
# time.sleep(5)
# test_case_2()
# time.sleep(5)
# test_case_3()
# time.sleep(5)
# test_case4()
# time.sleep(5)
# test_case5()
# time.sleep(5)
# test_case6()
# time.sleep(5)
# test_case7()
# time.sleep(5)
# test_case8()
# time.sleep(5)
# test_case9()
# time.sleep(5)
# test_case10()
# time.sleep(5)
# test_case11()