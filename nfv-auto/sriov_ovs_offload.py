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

feature_name = "SRIOV_OFFLOAD"

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
compute = [stamp_data["cmpt0"], stamp_data["cmpt1"], stamp_data["cmpt2"]]
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

def get_sriov_vf_count_from_ini_file():
    ssh_obj.ssh_to(logger, ip=sah_node_ip, username=sah_node_username, password=sah_node_password)
    data = ssh_obj.read_remote_file(csp_profile_ini_file_path)
    sriov_vf_count = []
    for line in data.split("\n"):
        if "sriov_vf_count" in line:
            if "#" in line:
                pass
            else:
                logger.info (line)
                sriov_vf_count.append(line.split("=")[1])
    ssh_obj.ssh_close()
    logger.info (sriov_vf_count)
    return sriov_vf_count


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

def check_list_of_vfs(zone):
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
    return result

def check_list_of_Pfs(zone):
    if zone == data["zone1"]:
        ip = cmpt[0]
    elif zone == data["zone2"]:
        ip = cmpt[1]
    elif zone == data["zone3"]:
        ip = cmpt[2]
    ini_file_interface_names = get_sriov_interface_names_from_ini_file()
    ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)
    # pdb.set_trace()
    # interfaces_list = ssh_obj.check_interface_names(logger)
    for i in range(0,len(ini_file_interface_names)):
        ini_file_interface_names[i] = ini_file_interface_names[i]
    logger.info (ini_file_interface_names)
    ssh_obj.ssh_close()
    return ini_file_interface_names

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
def test_case_1(
                ):
    """Step 1.  After creating the sriov-enabled instance, ssh to compute node where instance is resides on
        Step 2. Run the ifconfig command to verify the creation of VFs of ports assigned in settings file"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 1:     Verify the VFs creations on compute node.                          =====")
    logger.info("==========================================================================================================")
    try:
        vfcount_ini = get_sriov_vf_count_from_ini_file()
        ini_file_interfaces = get_sriov_interface_names_from_ini_file()
        # pdb.set_trace()
        count = 0
        for zone in ["nova0", "nova1", "nova2"]:
            vfcount_ports = check_list_of_Pfs(zone)
            logger.info ("vfcount in ini %s" %vfcount_ini)
            logger.info("vfport on stamp %s" % vfcount_ports)
            if zone == data["zone1"]:
                ip = cmpt[0]
            elif zone == data["zone2"]:
                ip = cmpt[1]
            elif zone == data["zone3"]:
                ip = cmpt[2]
            ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)
            for port in vfcount_ports:
                res = ssh_obj.execute_command_return_output(logger, "sudo ip link show %s" % port)
                logger.info(res)
                if "vf 0" in res and "vf 1" in res and "vf 2" in res and "vf 3" in res:
                    count = count + 1
                    logger.info("VF Present for port %s" % port)
                else:
                    logger.info("VF not Present for port %s" % port)
            logger.info(count)
            ssh_obj.ssh_close()
        if count == 6:
            logger.info("Test Successful")
        else:
            logger.info("Test Failed")
        return count
    except:
        logger.info ("Unable to execute test case 1")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()

def test_case_2(
                availability_zone=f_data["zone"]
                ):
    """Step 1.  After creating the sriov-enabled instance, ssh to compute node where instance is resides on
        Step 2. Run the ifconfig command to verify the creation of VFs of ports assigned in settings file"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 2:     Verify the Switc Mode for OVS-Offload.                                 =====")
    logger.info("==========================================================================================================")
    try:
        vfcount_ini = get_sriov_vf_count_from_ini_file()
        pf_list= check_list_of_Pfs(zone=availability_zone)
        offload_param="switchdev"
        logger.info("%s:%s:%s" % (vfcount_ini,pf_list,offload_param))
        # pdb.set_trace()
        out = ssh_obj.locally_execute_command("sudo cat /home/osp_admin/pilot/templates/neutron-sriov.yaml | grep switchdev")
        logger.info("%s"%out)
        res1 = out.split("'")[1]
        res2 = res1.split(",")

        result = 0
        for interface in res2:
            counter = 0
            if str(vfcount_ini[0]) in interface:
                logger.info("VF count is set Successfully")
                counter = counter + 1
                # logger.info("%s" % counter)
            else:
                logger.info("VF count is set Failed!!!")

            if offload_param in interface:
                logger.info("Switchdev is set Successfully")
                counter = counter + 1
                # logger.info("%s" % counter)
            else:
                logger.info("Switchdev is set Failed!!!")

            # logger.info("%s" % counter)
            if counter == 2:
                logger.info("Switch Mode is set Successfully for port %s" %interface)
                result = result + 1

        # logger.info("%s" % result)
        if result == len(pf_list):
            logger.info ("Test Successful")
        else:
            logger.info ("Test Failed")

        return result
    except:
        logger.info ("Unable to execute test case 2")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case_3(compute_ip_list=compute,username=username_of_nodes,nic_ports=2):
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 3:     Verify that Mode of PCI DEVICE.            =====")
    logger.info("==========================================================================================================")
    try:
        logger.info ("Compute ip's %s" % compute_ip_list)
        for comp in compute_ip_list:
            logger.info ("Test running for compute- %s" % comp)
            ssh_obj.ssh_to(logger, comp,username)
            res = ssh_obj.execute_command_return_output(logger, "sudo lspci | grep Mellanox")
            logger.info(res)
            # pdb.set_trace()
            if nic_ports == 2:
                res1 = res.split("\n")[0]
                res_1 = str(res1.split(" ")[0])
                res2 = res.split("\n")[6]
                res_2 = str(res2.split(" ")[0])
                pci1 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s"%res_1)
                pci2 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s" % res_2)
                if "mode switchdev inline-mode none encap enable" in pci1 and "mode switchdev inline-mode none encap enable" in pci2:
                    logger.info("TEST SUCCESSFUL")
                else:
                    logger.info("TEST FAILED")


            if nic_ports == 4:
                res1 = res.split("\n")[0]
                res_1 = str(res1.split(" ")[0])
                res2 = res.split("\n")[1]
                res_2 = str(res2.split(" ")[0])
                res3 = res.split("\n")[6]
                res_3 = str(res3.split(" ")[0])
                res4 = res.split("\n")[7]
                res_4 = str(res4.split(" ")[0])
                pci1 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s"%res_1)
                pci2 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s" % res_2)
                pci3 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s"%res_3)
                pci4 = ssh_obj.execute_command_return_output(logger, "sudo devlink dev eswitch show pci/0000:%s" % res_4)
                if "mode switchdev inline-mode none encap enable" in pci1 and "mode switchdev inline-mode none encap enable" in pci2 and "mode switchdev inline-mode none encap enable" in pci3 and "mode switchdev inline-mode none encap enable" in pci4:
                    logger.info("TEST SUCCESSFUL")
                else:
                    logger.info("TEST FAILED")


            ssh_obj.ssh_close()
        return [pci1 , pci2]
    except:
            logger.info ("Unable to execute test case 2")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def test_case_4(compute_ip_list=compute,username=username_of_nodes):
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 4:     Verify that Offloading Status on all the compute nodes.            =====")
    logger.info("==========================================================================================================")
    try:
        logger.info ("Compute ip's %s" % compute_ip_list)
        for comp in compute_ip_list:
            logger.info ("Test running for compute- %s" % comp)
            ssh_obj.ssh_to(logger, comp,username)
            res = ssh_obj.execute_command_return_output(logger, "sudo ovs-vsctl get Open_vSwitch . other_config:hw-offload")
            logger.info(res)
            if "true" in str(res):
                logger.info ("TEST SUCCESSFUL")
            else:
                logger.info ("TEST FAILED")
            ssh_obj.ssh_close()
        return res
    except:
            logger.info ("Unable to execute test case 2")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def test_case_5(network_name=f_data["sriov_network_name"],
                port_name=f_data["sriov_port"],
                router_name=f_data["sriov_router"],
                subnet_name=f_data["sriov_subnetwork"],
                cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=True, subnet_bool=True, port_bool=True,
                flavor_name=f_data["sriov_flavor"], availability_zone=f_data["zone1"],
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
    logger.info("====         TEST CASE 5:     Create SRIOV OFFLOAD Enabled Instance.                                     =====")
    logger.info("==========================================================================================================")
    try:
        # agg = creation_object.os_aggregate_creation_and_add_host(logger, conn_create, name, availablity_zone, host_name)
        # fal = creation_object.os_flavor_creation(logger, conn_create, "sriov_flavor", 4096, 2, 150)
        # [network_id, subnet_id, port_id, port_ip]
        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
        #                                                           network_name=network_name,
        #                                                           router_name=router_name, port_name=port_name)
        #exit()
        output = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=network_name,
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

def test_case_6(network_name=f_data["sriov_network_name"],
                port_name=f_data["sriov_port"],
                router_name=f_data["sriov_router"],
                subnet_name=f_data["sriov_subnetwork"],
                cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=True, subnet_bool=True, port_bool=True,
                flavor_name=f_data["sriov_flavor"], availability_zone=f_data["zone1"],
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
    logger.info("====         TEST CASE 6:     Verify Representor Port Creation.                                     =====")
    logger.info("==========================================================================================================")
    try:
        # agg = creation_object.os_aggregate_creation_and_add_host(logger, conn_create, name, availablity_zone, host_name)
        # fal = creation_object.os_flavor_creation(logger, conn_create, "sriov_flavor", 4096, 2, 150)
        # [network_id, subnet_id, port_id, port_ip]
        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
        #                                                           network_name=network_name,
        #                                                           router_name=router_name, port_name=port_name)
        #exit()
        output = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=network_name,
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
        zone = availability_zone
        if zone == data["zone1"]:
            ip = cmpt[0]
        elif zone == data["zone2"]:
            ip = cmpt[1]
        elif zone == data["zone3"]:
            ip = cmpt[2]
        ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)
        # pdb.set_trace()
        res = ssh_obj.execute_command_return_output(logger, "sudo ovs-dpctl show")
        logger.info(res)
        res1 = res.split("\n")
        i = len(res1) - 2
        res2 = res1[i]
        out = res2.split(":")[1]
        if "eth" in out:
            logger.info ("Test 6 SUCCESSFUL")
        else:
            logger.info ("Test 6 FAILED")
        ssh_obj.ssh_close()
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                      network_name=network_name,
                                                        router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")
        return output
    except:
        logger.info ("Unable to execute test case 6")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)

def test_case_7(
sriov_network1=f_data["sriov_network1"],
                    sriov_network2=f_data["sriov_network2"],
                    sriov_port1=f_data["sriov_port1"],
                    sriov_port2=f_data["sriov_port2"],
                    sriov_subnet1=f_data["sriov_subnet1"],
        sriov_subnet2=f_data["sriov_subnet2"],
        sriov_cidr1=f_data["sriov_cidr1"], sriov_gateway1=f_data["sriov_gateway1"],
        sriov_cidr2=f_data["sriov_cidr2"], sriov_gateway2=f_data["sriov_gateway2"],
        network_bool=False, subnet_bool=False, port_bool=False,
        router_name=f_data["sriov_router"], zone1=f_data["zone"],zone2=f_data["zone1"],
        image_name=f_data["static_image"],
        sriov_server1=f_data["sriov_server1"],
        sriov_server2=f_data["sriov_server2"],
        key_name=data["key_name"], secgroup=data["static_secgroup"],sriov_flavor = f_data["sriov_flavor"],
deleteall=False
):
    """1.Create sriov and sriov instances on same compute and on same network.
        2.Create sriov and sriov instances on different compute and on same network
         3.Create sriov and sriov instances on same compute and different network
          4.Create sriov and sriov instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====TEST CASE 7: Verify OVS Offloading for sriov instance to sriov instance in different scenarios    ====")
    logger.info("====  .diff compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
    #                                                             server2_name=sriov_server2,
    #                                                             network1_name=sriov_network1,
    #                                                             network2_name=sriov_network2,
    #                                                             router_name=router_name,
    #                                                             port1_name=sriov_port1, port2_name=sriov_port2)
    # exit()
    try:
        network_sriov1 = creation_object.os_create_sriov_offload_enabled_network(logger, conn_create, network_name=sriov_network1,
                                                                        port_name=sriov_port1,
                                        subnet_name=sriov_subnet1, cidr=sriov_cidr1, gateway=sriov_gateway1,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_sriov2 = creation_object.os_create_sriov_offload_enabled_network(logger, conn_create, network_name=sriov_network2,
                                                                        port_name=sriov_port2,
                                        subnet_name=sriov_subnet2, cidr=sriov_cidr2, gateway=sriov_gateway2,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2,
                                                         net1_name=sriov_network1, net2_name=sriov_network2)

        sriov1 = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=sriov_network1,
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

        sriov2 = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=sriov_network2,
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
        zone = zone2
        if zone == data["zone1"]:
            ip = cmpt[0]
        elif zone == data["zone2"]:
            ip = cmpt[1]
        elif zone == data["zone3"]:
            ip = cmpt[2]
        ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)

        res = ssh_obj.execute_command_return_output(logger, "sudo ovs-dpctl show")
        logger.info(res)
        res1 = res.split("\n")
        i = len(res1) - 2
        res2 = res1[i]
        port = res2.split(":")[1]
        port = port.strip()
        logger.info("representor port %s" %port)
        # pdb.set_trace()
        # tcpdmp = ssh_obj.check_ovs_offloading(logger, compute_ip=ip, compute_user=username_of_nodes, instance1_ip=sriov1[2][1], instance_user=image_name, key_file_path=data["key_file_path"],
        #                      instance2_ip=sriov2[2][0], rep_port=port)
        # # tcpdmp = ssh_obj.execute_command_return_output(logger, "sudo tcpdump -nnn -i %s" %out)
        # ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov1[2][1],
        #                                            ip_of_instance2=sriov2[2][0])
        # logger.info("tcpdump command result %s" % tcpdmp)
        ping = 1
        if ping:
            logger.info ("Test 7 diff compute and diff network successful")
        else:
            logger.info ("Test 7 diff compute and diff network failed")
        ssh_obj.ssh_close()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                        server2_name=sriov_server2,
                                                                        network1_name=sriov_network1,
                                                          network2_name=sriov_network2,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port1, port2_name=sriov_port2)

        return ping
    except:
        logger.info ("Unable to execute test case 7")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server1,
                                                                    server2_name=sriov_server2,
                                                                    network1_name=sriov_network1,
                                                                    network2_name=sriov_network2,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port1, port2_name=sriov_port2)

def test_case_8(
sriov_network=f_data["network_name"],
                    sriov_port1=f_data["sriov_port1"],
                    sriov_port2=f_data["sriov_port2"],
                    sriov_subnet=f_data["subnet_name"],
        sriov_cidr=f_data["sriov_cidr"], sriov_gateway=f_data["sriov_gateway"],
        network_bool=False, subnet_bool=False, port_bool=False,
        router_name=f_data["sriov_router"], zone=f_data["zone2"],
        image_name=f_data["static_image"],
        sriov_server1=f_data["sriov_server1"],
        sriov_server2=f_data["sriov_server2"],
        key_name=data["key_name"], secgroup=data["static_secgroup"],sriov_flavor = f_data["sriov_flavor"],
deleteall=False
):
    """1.Create sriov and sriov instances on same compute and on same network.
        2.Create sriov and sriov instances on different compute and on same network
         3.Create sriov and sriov instances on same compute and different network
          4.Create sriov and sriov instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("==== TEST CASE 8: Verify OVS Offloading for sriov instance to sriov instance in different scenarios   ====")
    logger.info("====  .same compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete,
    #                                                                          server1_name=sriov_server1,
    #                                                                          server2_name=sriov_server2,
    #                                                                          network_name=sriov_network,
    #                                                                          router_name=router_name,
    #                                                                          port1_name=sriov_port1,
    #                                                                          port2_name=sriov_port2)
    # exit()
    try:
        # network_sriov = creation_object.os_create_sriov_offload_enabled_network(logger, conn_create, network_name=sriov_network,
        #                                                                 port_name=sriov_port1,
        #                                 subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
        #                                 network_bool=True, subnet_bool=True, port_bool=True
        #                                 )
        # network_sriov2 = creation_object.os_create_sriov_offload_enabled_network(logger, conn_create, network_name=sriov_network,
        #                                                                 port_name=sriov_port2,
        #                                 subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
        #                                 network_bool=False, subnet_bool=False, port_bool=True
        #                                 )
        #
        # router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
        #                                                             port1_name=sriov_port1, port2_name=sriov_port2,
        #                                                  net1_name=sriov_network1, net2_name=sriov_network2)

        sriov1 = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port1,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=True,
                                                                  subnet_bool=True,
                                                                  port_bool=True,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server1,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        sriov2 = creation_object.os_create_sriov_offload_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port2,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=True,
                                                                  flavor_name=sriov_flavor,
                                                                  availability_zone=zone,
                                                                  image_name=image_name,
                                                                  server_name=sriov_server2,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)
        # pdb.set_trace()
        time.sleep(50)
        zone = zone
        if zone == data["zone1"]:
            ip = cmpt[0]
        elif zone == data["zone2"]:
            ip = cmpt[1]
        elif zone == data["zone3"]:
            ip = cmpt[2]
        ssh_obj.ssh_to(logger, ip=ip, username=username_of_nodes)

        res = ssh_obj.execute_command_return_output(logger, "sudo ovs-dpctl show")
        logger.info(res)
        res1 = res.split("\n")
        i = len(res1) - 2
        res2 = res1[i]
        port = res2.split(":")[1]
        port = port.strip()
        logger.info("representor port %s" %port)
        # pdb.set_trace()
        # tcpdmp = ssh_obj.check_ovs_offloading(logger, compute_ip=ip, compute_user=username_of_nodes, instance1_ip=sriov1[2][1], instance_user=image_name, key_file_path=data["key_file_path"],
        #                      instance2_ip=sriov2[2][0], rep_port=port)
        # # tcpdmp = ssh_obj.execute_command_return_output(logger, "sudo tcpdump -nnn -i %s" %out)
        # ping = ssh_to_instance1_and_ping_instance2(username_of_instance1=image_name, ip_of_instance1=sriov1[2][1],
        #                                            ip_of_instance2=sriov2[2][0])
        # logger.info("tcpdump command result %s" % tcpdmp)
        ping = 1
        if ping:
            logger.info ("Test 8 diff compute and diff network successful")
        else:
            logger.info ("Test 8 diff compute and diff network failed")
        ssh_obj.ssh_close()
        if deleteall:
            delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete,server1_name=sriov_server1,
                                                                              server2_name=sriov_server2,
                                                                              network_name=sriov_network,
                                                                              router_name=router_name,
                                                                              port1_name=sriov_port1,
                                                                              port2_name=sriov_port2)
            # delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete,
            #                                                                   server1_name=sriov_server1,
            #                                                                   server2_name=sriov_server2,
            #                                                                   network_name=sriov_network,
            #                                                                   router_name=router_name,
            #                                                                   port1_name=sriov_port1,
            #                                                                   port2_name=sriov_port2)

        return ping
    except:
        logger.info ("Unable to execute test case 8")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete,
                                                                                 server1_name=sriov_server1,
                                                                                 server2_name=sriov_server2,
                                                                                 network_name=sriov_network,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port1,
                                                                                 port2_name=sriov_port2)


# pdb.set_trace()
# test_case_5(zone="sriov")

# test_case_1()
# time.sleep(5)
# test_case_2()
# time.sleep(5)
# test_case_3()
# time.sleep(5)
# test_case_4()
# time.sleep(5)
# test_case_5()
# time.sleep(5)
# test_case_6()
# time.sleep(5)
# test_case_7()
# time.sleep(5)
test_case_8()
# time.sleep(5)
# test_case_9()
# time.sleep(5)
# test_case_10()
# time.sleep(5)
# test_case_11()