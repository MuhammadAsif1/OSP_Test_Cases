#!/usr/bin/python
import commands
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import iperf3_funcs
import pdb
import time
import openstack
import sys
import os
import json
#########################logger code start
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

feature_name = "OVSDPDK_SRIOV"

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
ssh_obj = ssh_functions()
creation_object = Os_Creation_Modules()
delete_object = Os_Deletion_Modules()

conn_create = creation_object.os_connection_creation()
conn_delete = delete_object.os_connection_creation()

feature_setup_file = "dpdk_sriov_setup.json"

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

def get_dpdk_interface_names_from_ini_file():
    ssh_obj.ssh_to(logger, ip=sah_node_ip, username=sah_node_username, password=sah_node_password)
    data = ssh_obj.read_remote_file(csp_profile_ini_file_path)
    interface_names = []
    for line in data.split("\n"):
        if "ComputeOvsDpdkInterface" in line:
            if "#" in line:
                pass
            else:
                logger.info( line)
                interface_names.append(line.split("=")[1])
    ssh_obj.ssh_close()
    logger.info( interface_names)
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
    logger.info(ini_file_interface_names)
    # pdb.set_trace()
    result = []
    for interface in interfaces_list:
        for i in ini_file_interface_names:
            if i in interface:
                result.append(interface)
                logger.info( interface)
    logger.info( result)
    vf_count = len(result)
    logger.info( vf_count)
    ssh_obj.ssh_close()
    return vf_count

def test_case_1(network_name, port_name,router_name, subnet_name, cidr, gateway,
                                        network_bool, subnet_bool, port_bool,
                                                            flavor_name,
                                                         availability_zone,
                                                         image_name,
                                                         server_name,
                                                         security_group_name,
                                                         key_name,
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
    logger.info("====         TEST CASE 1:     Create SRIOV Enabled Instance.                                     =====")
    logger.info("==========================================================================================================")
    try:
        # agg = creation_object.os_aggregate_creation_and_add_host(conn_create, name, availablity_zone, host_name)
        # fal = creation_object.os_flavor_creation(conn_create, "sriov_flavor", 4096, 2, 150)
        # [network_id, subnet_id, port_id, port_ip]
        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
        #                                                           network_name=network_name,
        #                                                           router_name=router_name, port_name=port_name)
        # exit()
        # for x in range(2,7):
        #     port_name="sriov_net1_port_%s"%x
        #     server_name="sriov-vm-%s"%x
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
            logger.info( "Test 1 SUCCESSFUL")
        else:
            logger.info( "Test 1 FAILED")
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                      network_name=network_name,
                                                        router_name=router_name, port_name=port_name)
        else:
            logger.info( "Note: Nothing is deleted!")
        return output
    except:
        logger.info( "Unable to execute test case 1(1)")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)



def test_case_2(network_name, port_name,router_name, subnet_name, cidr, gateway,
                                        network_bool, subnet_bool, port_bool,
                                                            flavor_name,
                                                         availability_zone,
                                                         image_name,
                                                         server_name,
                                                         security_group_name,
                                                         key_name):
    """Step 1.  After creating the sriov-enabled instance, ssh to compute node where instance is resides on
        Step 2. Run the ifconfig command to verify the creation of VFs of ports assigned in settings file"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 2:     Verify the VFs creations on compute node.                          =====")
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
            logger.info( "Total number of VF's %s" %vfcount_before_server_creation)
            logger.info( "1 VF is consumed when instance created....%s" %vfcount_after_server_creation)
            logger.info( "1 VF is returned when instance deleted....%s" %vfcount_after_server_deletion)
            logger.info ("Test Successful")
        else:
            logger.info ("server creation failed / server is not created on the given compute")
            logger.info ("Test Failed")
    except:
        logger.info ("Unable to execute test case 1(1)")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)
def test_case3(server1_name, server2_name, network_name, subnet_name, router_name, port1_name, port2_name, zone,
               cidr, gateway_ip, flavor_name, image_name, secgroup_name, key_name, deleteall=True):
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 3:     Creating Same Compute and network sriov Instances.                =====")
    logger.info("==========================================================================================================")
    """1. Create instance-1 and instance-2 on same network and compute node e.g compute0
        2. ssh to instance-1
         3. ping to instance-2's ip"""
    # delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(conn_delete, server1_name=server1_name,
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
        ssh_obj.ssh_to(logger, ip=output[0][2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, output[1][2][0])

        if ping==1:
            logger.info( "Test SUCCESSFUL")
        else:
            logger.info( "Test failed")

        ssh_obj.ssh_close( )

        if deleteall:
            delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                       server2_name=server2_name,
                                                                       network_name=network_name,
                                                                       router_name=router_name,
                                                                       port1_name=port1_name,
                                                                       port2_name=port2_name)
        return ping
    except:
        logger.info( "Unable to execute test case 19(35)")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_sriov_enabled_and_router_with_1_network(logger, conn_delete, server1_name=server1_name,
                                                                   server2_name=server2_name,
                                                                   network_name=network_name,
                                                                   router_name=router_name,
                                                                   port1_name=port1_name,
                                                                   port2_name=port2_name)

def test_case4(server1_name, server2_name, network_name, subnet_name, router_name, port1_name, port2_name, zone1, zone2,
               cidr, gateway_ip, flavor_name, image_name, secgroup_name, key_name, deleteall=True):
    """1. Create instance-1 and instance-2 on same network and different compute nodes e.g instance-1 on compute0 and instance-2 on compute1
        2. ssh to instance-1
         3. ping to instance-2's ip"""
    logger.info("==========================================================================================================")
    logger.info("====         TEST CASE 4:     Creating Different Compute and Same Network sriov Instances.           =====")
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
        ssh_obj.ssh_to(logger, ip=output[0][2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, output[1][2][0])

        if ping==1:
            logger.info ("Test SUCCESSFUL")
        else:
            logger.info ("Test failed")

        ssh_obj.ssh_close( )

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


def test_case5():
    """1. ssh to compute nodes.
        2. Run command "cat /var/lib/os-net-config/dpdk_mapping.yaml"
         3. Ports assigned to ovs-dpdk should be same as set in settings file"""
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 5:     Check the ports are assigned correctly to OVS-DPDK.                =====")
    logger.info("==========================================================================================================")
    # pdb.set_trace()
    for cmp in [cmpt[0], cmpt[1], cmpt[2]]:
        ssh_obj.ssh_to(logger, cmp, username_of_nodes)
        res = ssh_obj.execute_command_return_output(logger, "sudo cat /var/lib/os-net-config/dpdk_mapping.yaml")
        out = res.split("\n")
        logger.info (out)
        pp = []
        for port in out:
            if "name" in port:
                pp.append(port.split(":")[1].replace("\\r","").strip())
            else:
                pass

        logger.info (pp)
        inter_count = len(pp)
        interface_count = 0
        sha_dpdk_interfaces = get_dpdk_interface_names_from_ini_file()

        for int in sha_dpdk_interfaces:
            if int in pp:
                interface_count += 1
                logger.info (int)
            else:
                logger.info ("Interface %s Not Fount"%int)
                interface_count = 0
        ssh_obj.ssh_close()

        if inter_count == interface_count:
            logger.info ("Interface Matched Test Successful")
        else:
            logger.info ("Test Failed")

    return sha_dpdk_interfaces

def test_case6():
    """1. ssh to compute node.
        2. Run the command "sudo ovs-appctl bond/show" to check the available ports in OVS-DPDK"""
    logger.info("==========================================================================================================")
    logger.info("====        TEST CASE 6:    Check the Port assigned to OVS-DPDK are active after the deployment.      ====")
    logger.info("==========================================================================================================")
    for cmp in [cmpt[0], cmpt[1], cmpt[2]]:
        ssh_obj.ssh_to(logger, cmp, username_of_nodes)
        # pdb.set_trace()
        res = ssh_obj.execute_command_return_output(logger, "sudo ovs-appctl bond/show")
        # out = res.split("\n")
        logger.info (res)
        # pdb.set_trace()

        if "slave dpdk0: enabled" in res and "slave dpdk1: enabled" in res:
            logger.info ("TEST SUCCESSFUL")
        else:
            logger.info ("TEST Failed")
        #Need to insert the pass fail critaria
        ssh_obj.ssh_close()
    return res


def test_case7():
    """1. Go to compute node.
        2. Run the command "cat /etc/default/grub isolcpus" to check the number of vCPUs assigned to host and VMs.
         3. Run the command "ovs-appctl dpif-netdev/pmd-rxq-show" to show the assignment of OVS-DPDK interface to which cores."""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 7:    Check the physical cores present are distributed according to the specfication. ====")
    logger.info("==========================================================================================================")
    ssh_obj.ssh_to(logger, cmpt[0], username_of_nodes)
    res1 = ssh_obj.execute_command_return_output(logger, "cat /etc/default/grub | grep isolcpus")
    res = ssh_obj.execute_command_return_output(logger, "sudo ovs-appctl dpif-netdev/pmd-rxq-show")
    logger.info (res1)
    logger.info (res)
    # check the available ports in OVS-DPDK
    if "core_id 2:" in res and "core_id 3:" in res and "core_id 26:" in res and "core_id 27:" in res:
        logger.info("TEST SUCCESSFUL")
    else:
        logger.info ("TEST Failed")
    return [res1, res]

def test_case8(flavor_name, availability_zone, image_name, port_name, server_name, secgroup_name,
               network_name, router_name, subnet_name, cidr, gateway,
               deleteall=True):
    """CREATE OVS-DPDK ENABLED INSTANCE
      1. Go to compute node.
        2. scource <overcloudrc>
         3. Run the command "openstack flavor create <flavor-name> --disk 40 --ram 4096 --vcpu 6"
          4. Add metadata tags to newly created flavor "openstack flavor set <flavor-name> --property hw:cpu_policy=dedicated --property hw:cpu_thread_policy=require --property hw:mem_page_size=large --property hw:numa_nodes=1 --property hw:numa_mempolicy=preferred"
            5. Run the command "openstack server create --image <image name> --key-name ovs-dpdk --availability-zone <compute node > --nic net-id=<Ovs-DpDk net id> --flavor <Ovs DPDK flavor> <instance name>"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 8:Create an Instance on OVS-DPDK enabled compute node with all necessary metadata tags====")
    logger.info("====      i-e cpu_policy, cpu_thread_policy, mem_page_size, numa_nodes and numa_mempolicy in mode 2.. ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
    #                                                           network_name=network_name,
    #                                                           router_name=router_name, port_name=port_name)
    # exit()
    try:
        # flavor = creation_object.os_flavor_ovsdpdk_creation(logger, conn_create, name=flavor_name,
        #                                            ram=4096, vcpus=6, disk=40)
        output = creation_object.os_create_dpdk_enabled_instance(logger, conn_create,
                                                                 network_name=network_name,
                                                                 port_name=port_name,
                                                                 router_name=router_name,
                                                                 subnet_name=subnet_name,
                                                                 cidr=cidr, gateway=gateway,
                                        flavor_name=flavor_name,
                                        availability_zone=availability_zone,
                                        image_name=image_name,
                                        server_name=server_name,
                                        security_group_name=secgroup_name
                                        )
        time.sleep(10)
        ping = ssh_obj.locally_ping_check(logger, ip=output[2][1])
        if ping:
            logger.info ("Test 8 SUCCESSFUL")
        else:
            logger.info ("Test 8 FAILED")
        if deleteall:
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                      network_name=network_name,
                                                        router_name=router_name, port_name=port_name)
        else:
            logger.info ("Note: Nothing is deleted!")

        return output


    except:
        logger.info ("Unable to execute test case 8")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name=server_name,
                                                                  network_name=network_name,
                                                                  router_name=router_name, port_name=port_name)

def test_case9(network_name=f_data["network_name"],
                sriov_port=f_data["sriov_port"],
                dpdk_port=f_data["dpdk_port"],
                subnet_name=f_data["subnet_name"], cidr=f_data["cidr"], gateway=f_data["gateway"],
                network_bool=False, subnet_bool=False, port_bool=False,
                router_name=f_data["router_name"],
                zone=f_data["zone"], image=f_data["static_image"],
                sriov_flavor=f_data["static_flavor"], dpdk_flavor=f_data["ovsdpdk_flavor"],
                sriov_server=f_data["sriov_server"], dpdk_server=f_data["dpdk_server"],
                key_name=data["key_name"],
                secgroup=data["static_secgroup"],
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 9:     Ping an sriov instance to ovs-dpdk instance in different scenarios             ====")
    logger.info("====  .same compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)

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
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone, cidr=cidr,
                                                            gateway_ip=gateway, flavor_name=dpdk_flavor, image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        time.sleep(10)
        ssh_obj.ssh_to(logger, ip=sriov[2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, dpdk[3])

        if ping:
            logger.info ("Test 9 same compute and same network successful")
        else:
            logger.info ("Test 9 same compute and same network failed")

        ssh_obj.ssh_close()
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                             server2_name=dpdk_server,
                                                                             network_name=network_name,
                                                                             router_name=router_name,
                                                                             port1_name=sriov_port,
                                                                             port2_name=dpdk_port)
        return ping
    except:
        logger.info ("Unable to execute test case 9")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                                 server2_name=dpdk_server,
                                                                                 network_name=network_name,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port,
                                                                                 port2_name=dpdk_port)


def test_case10(
network_name, sriov_port, dpdk_port, subnet_name, cidr, gateway,
    network_bool, subnet_bool, port_bool, router_name, zone1, zone2, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 10:     Ping an sriov instance to ovs-dpdk instance in different scenarios            ====")
    logger.info("====  .diff compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)
    try:
        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=network_name,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=subnet_name,
                                                                  cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name="sanity_flavor",
                                                                  availability_zone=zone1,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone2, cidr=cidr,
                                                            gateway_ip=gateway, flavor_name="sanity_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        time.sleep(50)
        # pdb.set_trace()
        logger.info("==================================================")
        logger.info("==Ping from SR-IOV instance to OVS-DPDK Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=sriov[2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, dpdk[3])
        ssh_obj.ssh_close()
        logger.info("==================================================")
        logger.info("==Ping from OVS-DPDK instance to SR-IOV Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=dpdk[4], username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, sriov[2][0])
        if ping:
            logger.info ("Test 10 diff compute and same network successful")
        else:
            logger.info ("Test 10 diff compute and same network failed")

        ssh_obj.ssh_close()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                             server2_name=dpdk_server,
                                                                             network_name=network_name,
                                                                             router_name=router_name,
                                                                             port1_name=sriov_port,
                                                                             port2_name=dpdk_port)
        return ping
    except:
        logger.info("Unable to execute test case 10")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                                 server2_name=dpdk_server,
                                                                                 network_name=network_name,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port,
                                                                                 port2_name=dpdk_port)

def test_case11(
sriov_network, dpdk_network, sriov_port, dpdk_port, sriov_subnet, dpdk_subnet, sriov_cidr, sriov_gateway,
        dpdk_cidr, dpdk_gateway,
    network_bool, subnet_bool, port_bool, router_name, zone, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 11:     Ping an sriov instance to ovs-dpdk instance in different scenarios             ====")
    logger.info("====  .same compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_dpdk = creation_object.os_network_creation(logger, conn_create, net_name=dpdk_network,
                                                           cidr=dpdk_cidr,
                                                           subnet_name=dpdk_subnet,
                                                           gatewy=dpdk_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port,
                                                         net1_name=sriov_network, net2_name=dpdk_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name="sanity_flavor",
                                                                  availability_zone=zone,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=dpdk_network,
                                                                               subnet_name=dpdk_subnet,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone, cidr=dpdk_cidr,
                                                            gateway_ip=dpdk_gateway, flavor_name="sanity_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        time.sleep(50)
        logger.info("==================================================")
        logger.info("==Ping from SR-IOV instance to OVS-DPDK Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=sriov[2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, dpdk[3])
        ssh_obj.ssh_close()
        logger.info("==================================================")
        logger.info("==Ping from OVS-DPDK instance to SR-IOV Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=dpdk[4], username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, sriov[2][0])

        if ping:
            logger.info("Test 11 same compute and diff network successful")
        else:
            logger.info("Test 11 same compute and diff network failed")

        ssh_obj.ssh_close()
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=dpdk_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=dpdk_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=dpdk_port)

        return ping
    except:
        logger.info("Unable to execute test case 11")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=dpdk_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=dpdk_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port)

def test_case12(
sriov_network, dpdk_network, sriov_port, dpdk_port, sriov_subnet, dpdk_subnet, sriov_cidr, sriov_gateway,
        dpdk_cidr, dpdk_gateway,
    network_bool, subnet_bool, port_bool, router_name, zone1, zone2, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 12:     Ping an sriov instance to ovs-dpdk instance in different scenarios             ====")
    logger.info("====  .diff compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_dpdk = creation_object.os_network_creation(logger, conn_create, net_name=dpdk_network,
                                                           cidr=dpdk_cidr,
                                                           subnet_name=dpdk_subnet,
                                                           gatewy=dpdk_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port,
                                                         net1_name=sriov_network, net2_name=dpdk_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name="sanity_flavor",
                                                                  availability_zone=zone1,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=dpdk_network,
                                                                               subnet_name=dpdk_subnet,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone2, cidr=dpdk_cidr,
                                                            gateway_ip=dpdk_gateway, flavor_name="sanity_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        time.sleep(50)
        logger.info("==================================================")
        logger.info("==Ping from SR-IOV instance to OVS-DPDK Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=sriov[2][1],username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, dpdk[3])
        ssh_obj.ssh_close()
        logger.info("==================================================")
        logger.info("==Ping from OVS-DPDK instance to SR-IOV Instance==")
        logger.info("==================================================")
        ssh_obj.ssh_to(logger, ip=dpdk[4], username="centos", key_file_name=data["key_file_path"])
        ping = ssh_obj.simple_ping_check(logger, sriov[2][0])

        if ping:
            logger.info("Test 12 diff compute and diff network successful")
        else:
            logger.info("Test 12 diff compute and diff network failed")

        ssh_obj.ssh_close()
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=dpdk_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=dpdk_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=dpdk_port)

        return ping
    except:
        logger.info("Unable to execute test case 12")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=dpdk_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=dpdk_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port)
######################===================================================================###########################################
    #
    # #2.Create sriov and ovsdpdk instances on different compute and on same network
    # senario2 = creation_object.create_2_instances_on_dif_compute_same_network(conn_create, server1_name, server2_name, network_name, subnet_name,
    #                                                   router_name, port_name, zone1 ,zone2, cidr,
    #                                                   gateway_ip, flavor_name, image_name,
    #                                                   secgroup_name, assign_floating_ip=True)
    # ssh_obj.ssh_with_key(senario2[0],"centos", "~/key.pem")
    # ping = ssh_obj.simple_ping_check(senario2[3])
    #
    # if ping:
    #     logger.info() "Test 10 senario 2 same compute and same network successful"
    # else:
    #     logger.info() "Test 10 senario 2 same compute and same network failed"
    #
    # ssh_obj.ssh_close()
    #
    #
    #
    # #3.Create sriov and ovsdpdk instances on same compute and different network
    # senario3 = creation_object.create_2_instances_on_same_compute_dif_network(conn_create, server1_name, server2_name, network1_name, network2_name,
    #                                                   subnet1_name, subnet2_name,
    #                                                   router_name, port1_name, port2_name, zone, cidr1,
    #                                                   gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
    #                                                   secgroup_name, assign_floating_ip=True)
    # ssh_obj.ssh_with_key(senario3[0],"centos", "~/key.pem")
    # ping = ssh_obj.simple_ping_check(senario3[3])
    #
    # if ping:
    #     logger.info() "Test 10 senario 3 successful"
    # else:
    #     logger.info() "Test 10 senario 3  failed"
    #
    # ssh_obj.ssh_close()
    # #4.Create sriov and ovsdpdk instances on different compute and different network
    # senario4 = creation_object.create_2_instances_on_dif_compute_dif_network(conn_create, server1_name, server2_name, network1_name, network2_name,
    #                                                   subnet1_name, subnet2_name,
    #                                                   router_name, port1_name, port2_name, zone1, zone2, cidr1,
    #                                                   gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
    #                                                   secgroup_name, assign_floating_ip=True)
    # ssh_obj.ssh_with_key(senario4[0],"centos", "~/key.pem")
    # ping = ssh_obj.simple_ping_check(senario4[3])
    #
    # if ping:
    #     logger.info() "Test 10 senario 4 successful"
    # else:
    #     logger.info() "Test 10 senario 4  failed"
    #
    # ssh_obj.ssh_close()

def test_case13(network_name, sriov_port, dpdk_port, subnet_name, cidr, gateway,
            network_bool, subnet_bool, port_bool, router_name, zone, image,
                sriov_server, dpdk_server, key_name, secgroup,
            deleteall=True):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Install Iperf3 on the instances and Run test as both server and client on all instances in different scenario"""
    # 1.Create sriov and ovsdpdk instances on same compute and on same network.
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 13: Run iperf3 test of an sriov instance to ovs-dpdk instance in different scenarios  ====")
    logger.info("====     1.same compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete,
    #                                                                   server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    try:
        network = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=network_name,
                                                                  port_name=sriov_port,
                                                                  subnet_name=subnet_name, cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=True, subnet_bool=True,
                                                                  port_bool=True
                                                                  )
        # pdb.set_trace( )
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
                                                                 flavor_name="sanity_flavor",
                                                                 availability_zone=zone,
                                                                 image_name=image,
                                                                 server_name=sriov_server,
                                                                 security_group_name=secgroup,
                                                                 key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name,
                                                                               port_name=dpdk_port,
                                                                               zone=zone, cidr=cidr,
                                                                               gateway_ip=gateway,
                                                                               flavor_name="sanity_flavor",
                                                                               image_name=image,
                                                                               secgroup_name=secgroup,
                                                                               assign_floating_ip=True)
        # pdb.set_trace()
        ip_list = [sriov[2][1], sriov[2][0], dpdk[4], dpdk[3]]#========================[fip,pip,fip,pip]
        # pdb.set_trace()
        bandwidth = iperf3_funcs.check_bandwidth_through_private_ip(logger, ips_list=ip_list, udp_flag=False, username=image,
                                                           iperf_client_time=None, packet_size=None)

        if bandwidth is not None:
            logger.info("Test 13 same compute and same network successful")
        else:
            logger.info("Test 13 same compute and same network failed")

        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete,
                                                                              server1_name=sriov_server,
                                                                              server2_name=dpdk_server,
                                                                              network_name=network_name,
                                                                              router_name=router_name,
                                                                              port1_name=sriov_port,
                                                                              port2_name=dpdk_port)
        return bandwidth
    except:
        logger.info("Unable to execute test case 13")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                          server2_name=dpdk_server,
                                                                          network_name=network_name,
                                                                          router_name=router_name,
                                                                          port1_name=sriov_port,
                                                                          port2_name=dpdk_port)


def test_case14(
network_name, sriov_port, dpdk_port, subnet_name, cidr, gateway,
    network_bool, subnet_bool, port_bool, router_name, zone1, zone2, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 14: Run iperf3 test of an sriov instance to ovs-dpdk instance in different scenarios  ====")
    logger.info("====  .diff compute same network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)
    try:
        network = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=network_name,
                                                                  port_name=sriov_port,
                                                                  subnet_name=subnet_name, cidr=cidr,
                                                                  gateway=gateway,
                                                                  network_bool=True, subnet_bool=True,
                                                                  port_bool=True
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
                                                                  flavor_name="st_flavor",
                                                                  availability_zone=zone1,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=network_name,
                                                                               subnet_name=subnet_name,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone2, cidr=cidr,
                                                            gateway_ip=gateway, flavor_name="ovsdpdk_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        ip_list = [sriov[2][1], sriov[2][0], dpdk[4], dpdk[3]]#========================[fip,pip,fip,pip]
        # pdb.set_trace()
        bandwidth = iperf3_funcs.check_bandwidth_through_private_ip(logger, ips_list=ip_list, udp_flag=False, username=image,
                                                           iperf_client_time=None, packet_size=None)

        if bandwidth is not None:
            logger.info("Test 14 diff compute and same network successful")
        else:
            logger.info("Test 14 diff compute and same network failed")
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                             server2_name=dpdk_server,
                                                                             network_name=network_name,
                                                                             router_name=router_name,
                                                                             port1_name=sriov_port,
                                                                             port2_name=dpdk_port)
        return bandwidth
    except:
        logger.info("Unable to execute test case 14")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_1_network_2ports(logger, conn_delete, server1_name=sriov_server,
                                                                                 server2_name=dpdk_server,
                                                                                 network_name=network_name,
                                                                                 router_name=router_name,
                                                                                 port1_name=sriov_port,
                                                                                 port2_name=dpdk_port)

def test_case15(
sriov_network, dpdk_network, sriov_port, dpdk_port, sriov_subnet, dpdk_subnet, sriov_cidr, sriov_gateway,
        dpdk_cidr, dpdk_gateway,
    network_bool, subnet_bool, port_bool, router_name, zone, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 15: Run iperf3 test of an sriov instance to ovs-dpdk instance in different scenarios  ====")
    logger.info("====  .same compute diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
    #                                                             server2_name=dpdk_server,
    #                                                             network1_name=sriov_network,
    #                                                             network2_name=dpdk_network,
    #                                                             router_name=router_name,
    #                                                             port1_name=sriov_port, port2_name=dpdk_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_dpdk = creation_object.os_network_creation(logger, conn_create, net_name=dpdk_network,
                                                           cidr=dpdk_cidr,
                                                           subnet_name=dpdk_subnet,
                                                           gatewy=dpdk_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port,
                                                         net1_name=sriov_network, net2_name=dpdk_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name="st_flavor",
                                                                  availability_zone=zone,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=dpdk_network,
                                                                               subnet_name=dpdk_subnet,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone, cidr=dpdk_cidr,
                                                            gateway_ip=dpdk_gateway, flavor_name="ovsdpdk_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        ip_list = [sriov[2][1], sriov[2][0], dpdk[4], dpdk[3]]#========================[fip,pip,fip,pip]
        # pdb.set_trace()
        bandwidth = iperf3_funcs.check_bandwidth_through_private_ip(logger, ips_list=ip_list, udp_flag=False, username=image,
                                                           iperf_client_time=None, packet_size=None)

        if bandwidth is not None:
            logger.info("Test 15 same compute and diff network successful")
        else:
            logger.info("Test 15 same compute and diff network failed")
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=dpdk_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=dpdk_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=dpdk_port)

        return bandwidth
    except:
        logger.info("Unable to execute test case 15")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=dpdk_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=dpdk_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port)


def test_case16(
sriov_network, dpdk_network, sriov_port, dpdk_port, sriov_subnet, dpdk_subnet, sriov_cidr, sriov_gateway,
        dpdk_cidr, dpdk_gateway,
    network_bool, subnet_bool, port_bool, router_name, zone1, zone2, image, sriov_server, dpdk_server, key_name, secgroup,
deleteall=True
):
    """1.Create sriov and ovsdpdk instances on same compute and on same network.
        2.Create sriov and ovsdpdk instances on different compute and on same network
         3.Create sriov and ovsdpdk instances on same compute and different network
          4.Create sriov and ovsdpdk instances on different compute and different network
            5.Ping one instance to other in each scenario"""
    logger.info("==========================================================================================================")
    logger.info("====  TEST CASE 16: Run iperf3 test of an sriov instance to ovs-dpdk instance in different scenarios  ====")
    logger.info("====  .same diff diff network ====")
    logger.info("==========================================================================================================")
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                   server2_name=dpdk_server,
    #                                                                   network_name=network_name,
    #                                                                   router_name=router_name,
    #                                                                   port1_name=sriov_port,
    #                                                                   port2_name=dpdk_port)
    #1.Create sriov and ovsdpdk instances on same compute and on same network.
    ##############===============================SRIOV INSTANCE
    # delete_object.delete_2_instances_and_router_with_1_network_2ports(conn_delete, server1_name=sriov_server,
    #                                                                  server2_name=dpdk_server,
    #                                                                  network_name=network_name,
    #                                                                  router_name=router_name,
    #                                                                  port1_name=sriov_port,
    #                                                                  port2_name=dpdk_port)
    try:
        network_sriov = creation_object.os_create_sriov_enabled_network(logger, conn_create, network_name=sriov_network,
                                                                        port_name=sriov_port,
                                        subnet_name=sriov_subnet, cidr=sriov_cidr, gateway=sriov_gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        network_dpdk = creation_object.os_network_creation(logger, conn_create, net_name=dpdk_network,
                                                           cidr=dpdk_cidr,
                                                           subnet_name=dpdk_subnet,
                                                           gatewy=dpdk_gateway)

        router = creation_object.os_router_creation_with_2_networks(logger, conn_create, router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port,
                                                         net1_name=sriov_network, net2_name=dpdk_network)

        sriov = creation_object.os_create_sriov_enabled_instance(logger, conn_create, network_name=sriov_network,
                                                                  port_name=sriov_port,
                                                                  router_name=router_name,
                                                                  subnet_name=sriov_subnet,
                                                                  cidr=sriov_cidr,
                                                                  gateway=sriov_gateway,
                                                                  network_bool=network_bool,
                                                                  subnet_bool=subnet_bool,
                                                                  port_bool=port_bool,
                                                                  flavor_name="st_flavor",
                                                                  availability_zone=zone1,
                                                                  image_name=image,
                                                                  server_name=sriov_server,
                                                                  security_group_name=secgroup,
                                                                  key_name=key_name)

        dpdk = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
                                                                               network_name=dpdk_network,
                                                                               subnet_name=dpdk_subnet,
                                                                               router_name=router_name, port_name=dpdk_port,
                                                                               zone=zone2, cidr=dpdk_cidr,
                                                            gateway_ip=dpdk_gateway, flavor_name="ovsdpdk_flavor", image_name=image,
                                                            secgroup_name=secgroup, assign_floating_ip=True)
        # pdb.set_trace()
        ip_list = [sriov[2][1], sriov[2][0], dpdk[4], dpdk[3]]#========================[fip,pip,fip,pip]
        # pdb.set_trace()
        bandwidth = iperf3_funcs.check_bandwidth_through_private_ip(logger, ips_list=ip_list, udp_flag=False, username=image,
                                                           iperf_client_time=None, packet_size=None)

        if bandwidth is not None:
            logger.info("Test 16 diff compute and diff network successful")
        else:
            logger.info("Test 16 diff compute and diff network failed")
        # pdb.set_trace()
        if deleteall:
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                        server2_name=dpdk_server,
                                                                        network1_name=sriov_network,
                                                          network2_name=dpdk_network,
                                                          router_name=router_name,
                                                                        port1_name=sriov_port, port2_name=dpdk_port)

        return bandwidth
    except:
        logger.info("Unable to execute test case 16")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name=sriov_server,
                                                                    server2_name=dpdk_server,
                                                                    network1_name=sriov_network,
                                                                    network2_name=dpdk_network,
                                                                    router_name=router_name,
                                                                    port1_name=sriov_port, port2_name=dpdk_port)


























########################################################################################################################
"""
    senario1  = iperf3_funcs.create_2_instances_on_same_compute_same_network_and_exec_iperf3(assign_floating_ip=True,
                                                                    delete_after_create_flag=True,
                                                                    server1_name=server1_name,
                                                                    server2_name=server2_name,
                                                                    network_name=network_name,
                                                                    subnet_name=subnet_name, router_name=router_name,
                                                                    port_name=port_name, zone=zone,
                                                                    cidr=cidr, gateway_ip=gateway_ip,
                                                                    flavor_name=static_flavor,
                                                                    image_name=static_image,
                                                                    secgroup_name=static_secgroup)
    if senario1:
        logger.info() "Test 11 senario 1 successful BW = %s"%senario1
    else:
        logger.info() "Test 11 senario 1  failed"

    # 2.Create sriov and ovsdpdk instances on different compute and on same network
    senario2 = iperf3_funcs.create_2_instances_on_diff_compute_same_network_and_exec_iperf3(assign_floating_ip=True,
                                                                                            delete_after_create_flag=True,
                                                                                            server1_name=server1_name,
                                                                                            server2_name=server2_name,
                                                                                            network_name=network_name,
                                                                                            subnet_name=subnet_name,
                                                                                            router_name=router_name,
                                                                                            port_name=port_name,
                                                                                            zone1=zone1, zone2=zone2, cidr=cidr,
                                                                                            gateway_ip=gateway_ip,
                                                                                            flavor_name=static_flavor,
                                                                                            image_name=static_image,
                                                                                            secgroup_name=static_secgroup)
    if senario2:
        logger.info() "Test 11 senario 2 successful BW = %s"%senario2
    else:
        logger.info() "Test 11 senario 2  failed"

    # 3.Create sriov and ovsdpdk instances on same compute and different network
    senario3 = iperf3_funcs.create_2_instances_on_same_compute_diff_network_and_exec_iperf3(assign_floating_ip=True, delete_after_create_flag=True,
                                            server1_name=server1_name, server2_name=server2_name,
                                            network1_name=network1_name, network2_name=network2_name, subnet1_name=subnet1_name,
                                            subnet2_name=subnet2_name, router_name=router_name, port1_name=port1_name,
                                            port2_name=port2_name, zone=zone, cidr1=cidr1, gateway_ip1=gateway_ip1,
                                            cidr2=cidr2, gateway_ip2=gateway_ip2, flavor_name=static_flavor, image_name=static_image,
                                            secgroup_name=static_secgroup)
    if senario3:
        logger.info() "Test 11 senario 3 successful BW = %s"%senario3
    else:
        logger.info() "Test 11 senario 3  failed"

    # 4.Create sriov and ovsdpdk instances on different compute and different network
    senario4 = iperf3_funcs.create_2_instances_on_diff_compute_diff_network_and_exec_iperf3(assign_floating_ip=True, delete_after_create_flag=True,
                                            server1_name=server1_name, server2_name=server2_name,
                                            network1_name=network1_name, network2_name=network2_name, subnet1_name=subnet1_name,
                                            subnet2_name=subnet2_name, router_name=router_name, port1_name=port1_name,
                                            port2_name=port2_name, zone1=zone1, zone2=zone2, cidr1=cidr1, gateway_ip1=gateway_ip1,
                                            cidr2=cidr2, gateway_ip2=gateway_ip2,
                                            flavor_name=static_flavor, image_name=static_image, secgroup_name=static_secgroup)
    if senario4:
        logger.info() "Test 11 senario 4 successful BW = %s"%senario4
    else:
        logger.info() "Test 11 senario 4  failed"

    return [senario1, senario2, senario3, senario4]

"""
network_name = "sriov_net_1"
port_name = "sriov_net1_port_8"
subnet_name = "sriov_subnet_1"
cidr = "192.168.100.0/24"
gateway = "192.168.100.1"
network_bool = False
subnet_bool = False
port_bool = True
flav_name = "sanity_flavor"
zone    = "nova2"
image_name= "centos"
server_name = "sriov-vm8"
sec_group_name="b0842a1d-901b-4a85-8fe7-c3e2ecbe2eb8"
key_name = "ssh-key"
router_name="sriov_router_1"
#
#
#
test_case_1(network_name, port_name,router_name, subnet_name=subnet_name, cidr=cidr, gateway=gateway,
                                        network_bool=network_bool, subnet_bool=subnet_bool, port_bool=port_bool,
                                                            flavor_name=flav_name,
                                                         availability_zone=zone,
                                                         image_name=image_name,
                                                         server_name=server_name,
                                                         security_group_name=sec_group_name,
                                                         key_name=key_name, deleteall=False)
# time.sleep(2)
# test_case_2(network_name, port_name,router_name, subnet_name=subnet_name, cidr=cidr, gateway=gateway,
#                                         network_bool=network_bool, subnet_bool=subnet_bool, port_bool=port_bool,
#                                                             flavor_name=flav_name,
#                                                          availability_zone=zone,
#                                                          image_name=image_name,
#                                                          server_name=server_name,
#                                                          security_group_name=sec_group_name,
#                                                          key_name=key_name)
# time.sleep(2)
# test_case3(server1_name="senario1_vm_1",
#            server2_name="senario1_vm_2",
#            network_name="senario1_sriov_net1",
#            subnet_name="senario1_sriov_subnet1",
#            router_name="senario1_sriov_router",
#            port1_name="senario1_sriov_port1",
#            port2_name="senario1_sriov_port2",
#            zone="nova0",
#            cidr="192.168.200.0/24",
#            gateway_ip="192.168.200.1",
#            flavor_name="sanity_flavor",
#            image_name="centos",
#            secgroup_name="b0842a1d-901b-4a85-8fe7-c3e2ecbe2eb8",
#            key_name="ssh-key",
#            deleteall=True)
# time.sleep(2)
# test_case4(server1_name="senario2_vm_1",
#            server2_name="senario2_vm_2",
#            network_name="senario2_sriov_net1",
#            subnet_name="senario2_sriov_subnet1",
#            router_name="senario2_sriov_router",
#            port1_name="senario2_sriov_port1",
#            port2_name="senario2_sriov_port2",
#            zone1="nova1",zone2="nova2",
#            cidr="192.168.210.0/24",
#            gateway_ip="192.168.210.1",
#            flavor_name="sanity_flavor",
#            image_name="centos",
#            secgroup_name="b0842a1d-901b-4a85-8fe7-c3e2ecbe2eb8",
#            key_name="ssh-key",
#            deleteall=True)
# time.sleep(2)
# test_case5()
# time.sleep(2)
# test_case6()
# time.sleep(2)
# test_case7()
# time.sleep(2)
fla = "sanity_flavor"
zone="nova0"
img="centos"
secg="b0842a1d-901b-4a85-8fe7-c3e2ecbe2eb8"
por="dpdk_port1"
net="dpdk_net_1"
ser="dpdk_server_1"
rout="dpdk_router"
# network_name = "sriov_net_1"
# port_name = "sriov_net1_port_2"
subnet_name = "dpdk_subnet_1"
cidr = "192.168.100.0/24"
gateway = "192.168.100.1"
# network_bool = False
# subnet_bool = False
# port_bool = True
# flav_name = "sanity_flavor"
# zone    = "nova0"
# image_name= "centos"
# server_name = "sriov_vm_2"
# sec_group_name = "st_secgroup"
# key_name = "static_key"
# router_name="sriov_router_1"


# test_case8(flavor_name=fla, availability_zone=zone, image_name=img, port_name=por,
#            server_name=ser, secgroup_name=secg,
#                network_name=net, router_name=rout, subnet_name=subnet_name, cidr=cidr, gateway=gateway,
#                deleteall=False)
# time.sleep(2)
#####################################################################################################################
# test_case9()

# time.sleep(2)
# test_case10(
# network_name="sriov_dpdk_net", sriov_port="s_port", dpdk_port="d_port", subnet_name="sriov_dpdk_subnet",
#     cidr="192.168.70.0/24", gateway="192.168.70.1",
#     network_bool=True, subnet_bool=True, port_bool=True, router_name="sriov_dpdk_router", zone1="nova0", zone2="nova2",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"]
# )
# time.sleep(2)
# test_case11(
# sriov_network="sriov_dpdk_net1", dpdk_network="sriov_dpdk_net2", sriov_port="s_port", dpdk_port="d_port",
#     sriov_subnet="sriov_dpdk_subnet1", dpdk_subnet="sriov_dpdk_subnet2",
#     sriov_cidr="192.168.70.0/24", sriov_gateway="192.168.70.1",
#         dpdk_cidr="192.168.80.0/24", dpdk_gateway="192.168.80.1",
#     network_bool=False, subnet_bool=False, port_bool=False,
#     router_name="sriov_dpdk_router", zone="nova2",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
# deleteall=True
# )
# time.sleep(2)
# test_case12(
# sriov_network="sriov_dpdk_net1", dpdk_network="sriov_dpdk_net2", sriov_port="s_port", dpdk_port="d_port",
#     sriov_subnet="sriov_dpdk_subnet1", dpdk_subnet="sriov_dpdk_subnet2",
#     sriov_cidr="192.168.70.0/24", sriov_gateway="192.168.70.1",
#         dpdk_cidr="192.168.80.0/24", dpdk_gateway="192.168.80.1",
#     network_bool=False, subnet_bool=False, port_bool=False,
#     router_name="sriov_dpdk_router", zone1="nova1", zone2="nova2",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
# deleteall=True
# )
# test_case13(
#         network_name="sriov_dpdk_net", sriov_port="s_port", dpdk_port="d_port", subnet_name="sriov_dpdk_subnet",
#     cidr="192.168.70.0/24", gateway="192.168.70.1",
#     network_bool=False, subnet_bool=False, port_bool=False, router_name="sriov_dpdk_router", zone="nova0",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
#             deleteall=True)
# logger.info() "wait 20 sec....."
# time.sleep(20)
# logger.info() "Start Executing Next Case....."
# test_case14(
#         network_name="sriov_dpdk_net", sriov_port="s_port", dpdk_port="d_port", subnet_name="sriov_dpdk_subnet",
#     cidr="192.168.70.0/24", gateway="192.168.70.1",
#     network_bool=False, subnet_bool=False, port_bool=False, router_name="sriov_dpdk_router", zone1="nova0", zone2="nova1",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
#             deleteall=True)
# logger.info() "wait 20 sec....."
# time.sleep(20)
# logger.info() "Start Executing Next Case....."
# test_case15(
# sriov_network="sriov_dpdk_net1", dpdk_network="sriov_dpdk_net2", sriov_port="s_port", dpdk_port="d_port",
#     sriov_subnet="sriov_dpdk_subnet1", dpdk_subnet="sriov_dpdk_subnet2",
#     sriov_cidr="192.168.70.0/24", sriov_gateway="192.168.70.1",
#         dpdk_cidr="192.168.80.0/24", dpdk_gateway="192.168.80.1",
#     network_bool=False, subnet_bool=False, port_bool=False,
#     router_name="sriov_dpdk_router", zone="nova0",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
# deleteall=True
# )

# time.sleep(20)

# test_case16(
# sriov_network="sriov_dpdk_net1", dpdk_network="sriov_dpdk_net2", sriov_port="s_port", dpdk_port="d_port",
#     sriov_subnet="sriov_dpdk_subnet1", dpdk_subnet="sriov_dpdk_subnet2",
#     sriov_cidr="192.168.60.0/24", sriov_gateway="192.168.60.1",
#         dpdk_cidr="192.168.80.0/24", dpdk_gateway="192.168.80.1",
#     network_bool=False, subnet_bool=False, port_bool=False,
#     router_name="sriov_dpdk_router", zone1="nova0", zone2="nova1",
#     image="centos", sriov_server="s_instance", dpdk_server="d_instance",
#     key_name=data["key_name"], secgroup=data["static_secgroup"],
# deleteall=True
# )