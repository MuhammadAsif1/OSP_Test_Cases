#!/usr/bin/python
import commands
from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules
from delete_os import Os_Deletion_Modules
import iperf3_funcs
import pdb
import time
import openstack
import sys
import os
import json
import time
#########################logger code start
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

feature_name = "VLAN_AWARE_VM"

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

if os.path.exists("vlan_aware_setup.json"):
    vlan_data = None
    try:
        with open('vlan_aware_setup.json') as data_file:
            vlan_data = json.load(data_file)
        vlan_data = {str(i): str(j) for i, j in vlan_data.items()}
    except:
        print "\nFAILURE!!! error in vlan_aware_setup.json file!"

else:
    print ("\nFAILURE!!! vlan_aware_setup.json file not found!!!\nUnable to execute script\n\n")

def test_case1():
    """"1. ssh to controller node
        2. $ sudo docker ps | grep neutron
        3. $ sudo docker exec -it <neutron_api_contid> bash
        4. # cat /etc/neutron/neutron.conf | grep service_plugins"""

    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 1:      Verify trunk plugin is enabled in controller nodes.         =====")
    print("==========================================================================================================")
    try:
        ssh_obj.ssh_to(logger, "192.168.120.30","heat-admin")
        res = ssh_obj.execute_command_return_output(logger, "sudo docker ps | grep neutron_api")
        out = res.split("\n")
        #print out
        l3_agent_id_control = str(out[0].split(" ")[0])
        #print l3_agent_id_control.strip()
        res = ssh_obj.execute_command_return_output(logger, "sudo docker exec -t %s cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf | grep \"service_plugins\"" %l3_agent_id_control)
        # res1 = ssh_obj.execute_command_return_output(logger, "sudo docker exec --help")
        # print res1
        # res = ssh_obj.execute_command_return_output(logger, "sudo docker exec -t cbc18421d202 cat /etc/neutron/l3_agent.ini")
        #print res.split("\n")
        if "trunk" in str(res):
            print ("TEST SUCCESSFUL")
        else:
            print ("TEST FAILED")
        ssh_obj.ssh_close()
        return res
    except:
        print "Unable to execute test case 1"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def test_case2():
    """Run the following command to verify the trunk extension:
        $ openstack extension list --network | grep -i trunk"""
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 2:      Check if the API extensions are enabled.                    =====")
    print("==========================================================================================================")
    try:
        res = ssh_obj.locally_execute_command(logger, "openstack extension list --network | grep -i trunk")
        if "enabled" in str(res):
            print ("TEST SUCCESSFUL")
        else:
            print ("TEST FAILED")
        ssh_obj.ssh_close()
        return res
    except:
        print "Unable to execute test case 11"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def test_case3(delete_all=False):
    """1. ssh to director node.
        2. To create the parent ports, execute the following command:
      $ openstack port create --network <network-name> <port name>
        3. Create  trunks using the parent ports
      $ openstack network trunk create --parent-port <parent-port-name> <trunk-name>
        4. Next step is the creation of sub-ports for the trunk ports:
      $ openstack port create --network <network-name> --mac-address <mac-addr-of-parent-port> <subport-name>
        5. Associate the subports to the desired trunk port
      $ openstack network trunk set --subport port=<sub-portname>,segmentation-type=vlan,segmentation-id=210 <trunk-name>
        6. Now create vms using parent-ports
      $ openstack server create --nic port-id=<parent-port> --key-name <key-name> --image rhel --flavor m1.small vm1
        7. ssh to vm-1
      $ sudo -i
        # cd /etc/sysconfig/network-scripts/
        # cp ifcfg-eth0 ifcfg-eth0.210
        # cp ifcfg-eth0 ifcfg-eth0.220
        # vi ifcfg-eth0.210
        #vi ifcfg-eth0.220
        # cat ifcfg-eth0.210                                                REPLACED PARAMS
    DEVICE="eth0.210"                                                       DEVICE="eth0.210"
    BOOTPROTO="dhcp"                                                        BOOTPROTO=none
    BOOTPROTOv6="dhcp"                                                      IPADDR=sub-port-IP
    ONBOOT="yes"                                                            ONBOOT=yes
    USERCTL="yes"                                                           USERCTL=yes
    PEERDNS="yes"                                                           PEERDNS=no
    IPV6INIT="yes"                                                          NETMASK=255.255.255.0
    PERSISTENT_DHCLIENT="1"                                                 DEFROUTE=no
    VLAN=yes                                                                VLAN=yes
        8. # cat ifcfg-eth0.220
    DEVICE="eth0.220"
    BOOTPROTO="dhcp"
    BOOTPROTOv6="dhcp"
    ONBOOT="yes"
    USERCTL="yes"
    PEERDNS="yes"
    IPV6INIT="yes"
    PERSISTENT_DHCLIENT="1"
    VLAN=yes
        9. up the vlan-interfaces
        # ifup eth0.210
        # ifup eth0.220
        # ip a
        10. Create another instance as vm-2
        11. ssh to Vm-2
        12.Repeat the same procedure for the vm-2 and ping from vm2 the interfaces eth0.210 and eth0.220 of vm1
        13. ping -I <interface-of-vm1-in-same-vlan> <ip-address-of-interface>
            e.g "ping -I eth0.210 192.168.210.19"
    Trunk port creation API defination
        $ openstack port create --network last vlanvm_port #######PARENT PORT CREATION###########
        $ openstack network trunk  create --parent-port vlanvm_port --subport port=vlanvm_port,segmentation-type=vlan,segmentation-id=200 vlanvm_trunk """
    parent_network = vlan_data["parent_network"]
    parentport_name = vlan_data["parentport_name"]
    subport_network = vlan_data["subport_network"]
    subport_name = vlan_data["subport_name"]
    trunk_name = vlan_data["trunk_name"]
    flavor_name = vlan_data["static_flavor"]
    availability_zone = vlan_data["zone3"]
    image_name = vlan_data["static_image"]
    server_name = vlan_data["server_name"]
    security_group = vlan_data["static_secgroup"]
    segmentation_id = vlan_data["segmentation_id"]
    segmentation_type = vlan_data["segmentation_type"]
    old_eth_file_path = vlan_data["old_eth_file_path"]
    old_route_file_path = vlan_data["old_route_file_path"]
    gateway = vlan_data["gateway"]
    metricnumber=vlan_data["metricnumber"]
    key_file_path=vlan_data["key_file_path"]
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 3:      Launch the instance with the vlan aware interface.          =====")
    print("==========================================================================================================")
    # output = None
    # net_info = creation_object.os_network_creation(logger, conn_create, vlan_data["parent_network"], data["static_cidr"], data["static_subnet"],
    #                                    data["static_gateway"])
    # # ,provider_dic={ 'network_type': 'vlan','physical_network' : 'physint', 'segmentation_id': 205 })
    # logger.info(net_info)
    # os.system("openstack network list")
    # os.system("openstack network show %s" % data["static_network"])
    # # pdb.set_trace()
    # net_data = str(net_info)
    # seg_id = net_data.split(",")[11].strip()
    # segmentation_id = seg_id.split("=")[1].strip()
    # logger.info(seg_id)
    # logger.info("Creating Parent Network")
    # os.system("openstack network create --provider-network-type vlan --provider-physical-network physint --provider-segment 219 parent_network")
    # os.system("openstack subnet create --network parent_network --subnet-range 192.168.10.0/24 parent_subnet")
    # logger.info("Creating Sub Network")
    # os.system("openstack network create --provider-network-type vlan --provider-physical-network physint --provider-segment 220 sub_network")
    # os.system("openstack subnet create --network sub_network --subnet-range 192.168.90.0/24 sub_subnet")
    # logger.info("Attaching Network to Router")
    # os.system("openstack  router add subnet router parent_subnet")
    # os.system("openstack router add subnet router sub_subnet")
    # os.system("openstack network list | grep network")
    # os.system("openstack port list | grep subnet")
    # os.system("openstack router list")

    new_eth_file_path = "/etc/sysconfig/network-scripts/ifcfg-eth0.%s" % vlan_data["segmentation_id"]
    new_route_file_path = "/etc/sysconfig/network-scripts/route-eth0.%s" % vlan_data["segmentation_id"]
    try:
        # pdb.set_trace()
        output =  creation_object.os_create_vlan_aware_instance(logger, conn_create, parent_network=parent_network,
                                                                parentport_name=parentport_name,
                                                                subport_network=subport_network,
                                                                subport_name=subport_name,
                                                                trunk_name=trunk_name,
                                                                flavor_name=flavor_name,
                                                                availability_zone=availability_zone,
                                                                image_name=image_name,
                                                                server_name=server_name,
                                                                sec_group=security_group,
                                                                segmentation_id=segmentation_id,
                                                                segmentation_type=segmentation_type)
        server_ip = output[2]
        print server_ip
        subport_ip = output[3]
        print subport_ip
        ssh_obj.ssh_vlan_aware_vm(logger, ip_of_instance=server_ip,
                                  username_of_instance=image_name,
                                  key_file_path=key_file_path,
                                  new_eth_file_path=new_eth_file_path,
                                  new_route_file_path=new_route_file_path,
                                  subport_ip=subport_ip,
                                  old_eth_file_path=old_eth_file_path,
                                  old_route_file_path=old_route_file_path,
                                  gateway=gateway,
                                  segmentation_id=segmentation_id,
                                  metricnumber=metricnumber)

        if delete_all:
            delete_object.os_delete_server(logger, conn_delete, server_name=server_name)
            os.system("bash /home/osp_admin/NFV_window/nfv-auto/delete-trunks.sh %s %s %s"%(trunk_name,
                                                                                                 parentport_name,
                                                                                                 subport_name))
        return output
    except:
        print "Unable to execute test case 3"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        # dele = delete_object.os_delete_vlanaware_server(logger, conn_delete, server_name, parentport_name, subport_name, trunk_name, delete_parentport=True, delete_subport=True, delete_trunk=True, network_name=None)
        delete_object.os_delete_server(logger, conn_delete, server_name=server_name)
        os.system("bash /home/osp_admin/NFV_window/nfv-auto/delete-trunks.sh %s %s %s" % (trunk_name, parentport_name, subport_name))
        return output

def test_case4():
    """1. ssh to controller
        2. sudo ip netns exec <dhcp namespace> -i <key-location> username@ip-address"""
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 4:      ssh to vlan aware instance with tenant-network address.     =====")
    print("==========================================================================================================")
    try:
        # instance_private_ip =
        ssh_obj.ssh_to(logger, controller_ip,"heat-admin")
        res = ssh_obj.execute_command_show_output(logger, "sudo ip netns exec qdhcp-%s ssh -i ssh-key.pem centos@%s"%(namespace_id, instance_private_ip))
        res = ssh_obj.execute_command_show_output(logger, "ifconfig")
        if instance_private_ip in res:
            print ("TEST SUCCESSFUL")
        else:
            print("TEST FAILED")
        ssh_obj.ssh_close()

        return instance_private_ip
    except:
        print "Unable to execute test case 11"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case5():
    """1. ssh to director node
        2. Assign the vlan aware instance a floating ip through horizon.
         3. ssh -i <key-name> username@floating-ip"""
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 5:      ssh to vlan aware instance through floating-ip.             =====")
    print("==========================================================================================================")
    try:
        # instance_private_ip =
        ssh_obj.ssh_with_key(logger, instance_floating_ip, username="centos", key_file_name="~/ssh-key.pem")
        res = ssh_obj.execute_command_show_output(logger, "ifconfig")
        if instance_private_ip in res:
            print ("TEST SUCCESSFUL")
        else:
            print("TEST FAILED")
        ssh_obj.ssh_close()
        return instance_private_ip
    except:
        print "Unable to execute test case 11"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case6():
    parent_network1 = vlan_data["parent_network"]
    parent_network2 = vlan_data["parent_network1"]
    parentport_name1 = vlan_data["parentport_name"]
    parentport_name2 = vlan_data["parentport_name1"]
    subport_network = vlan_data["subport_network"]
    subport_name1 = vlan_data["subport_name"]
    subport_name2 = vlan_data["subport_name1"]
    trunk_name = vlan_data["trunk_name"]
    flavor_name = vlan_data["static_flavor"]
    availability_zone = vlan_data["zone3"]
    image_name = vlan_data["static_image"]
    server_name1 = vlan_data["server_name"]
    server_name2 = vlan_data["server_name1"]
    security_group = vlan_data["static_secgroup"]
    segmentation_id = vlan_data["segmentation_id"]
    segmentation_type = vlan_data["segmentation_type"]
    old_eth_file_path = vlan_data["old_eth_file_path"]
    old_route_file_path = vlan_data["old_route_file_path"]
    gateway = vlan_data["gateway"]
    metricnumber=vlan_data["metricnumber"]
    key_file_path=vlan_data["key_file_path"]
    interface = "eth0.%s"%segmentation_id
    """Create two instances from different parent ports and ping the vm-1's vlan-interface ip from vm-2's interface on the same vlan network"""
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 6:Create two instances from different parent ports                  =====")
    print("====         Ping the vm-1's vlan-interface ip from vm-2's interface on the same vlan network        =====")
    print("==========================================================================================================")
    try:
        print("========             SERVER 1 CREATING WITH DIFFERENT PARENT PORT                                =====")
        output = creation_object.os_create_vlan_aware_instance(logger, conn_create, parent_network=parent_network1,
                                                               parentport_name=parentport_name1,
                                                               subport_network=subport_network,
                                                               subport_name=subport_name1,
                                                               trunk_name=trunk_name,
                                                               flavor_name=flavor_name,
                                                               availability_zone=availability_zone,
                                                               image_name=image_name,
                                                               server_name=server_name1,
                                                               sec_group=security_group,
                                                               segmentation_id=segmentation_id,
                                                               segmentation_type=segmentation_type)

        pdb.set_trace()
        server_ip = output[2]
        subport_ip = output[3]
        ssh_obj.ssh_vlan_aware_vm(logger, server_ip, old_eth_file_path, new_eth_file_path, old_route_file_path,
                                  new_route_file_path, subport_ip, gateway, segmentation_id, metricnumber)
        ssh_obj.ssh_close()
        print("========             SERVER 2 CREATING WITH DIFFERENT PARENT PORT                                =====")
        res = creation_object.os_create_vlan_aware_instance(logger, conn_create, parent_network=parent_network2,
                                                               parentport_name=parentport_name2,
                                                               subport_network=subport_network,
                                                               subport_name=subport_name2,
                                                               trunk_name=trunk_name,
                                                               flavor_name=flavor_name,
                                                               availability_zone=availability_zone,
                                                               image_name=image_name,
                                                               server_name=server_name2,
                                                               sec_group=security_group,
                                                               segmentation_id=segmentation_id,
                                                               segmentation_type=segmentation_type)

        pdb.set_trace()
        server_ip1 = res[2]
        subport_ip1 = res[3]
        ssh_obj.ssh_vlan_aware_vm(logger, server_ip1, old_eth_file_path, new_eth_file_path, old_route_file_path,
                                  new_route_file_path, subport_ip1, gateway, segmentation_id, metricnumber)
        ssh_obj.ssh_close()
        ssh_obj.ssh_to(logger, ip=instance_floating_ip, username="centos", key_file_name=key_file_path)
        ping = simple_ping_check_using_inteface(logger, subport_ip1, interface)
        time.sleep(50)

        if ping == 1:
            logger.info("Test SUCCESSFUL")
        else:
            logger.info("Test failed")

        ssh_obj.ssh_close()
        ssh_obj.ssh_close()
        return instance_private_ip
    except:
        print "Unable to execute test case 11"
        print ("\nError: " + str(sys.exc_info()[0]))
        print ("Cause: " + str(sys.exc_info()[1]))
        print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case7():
    parent_network1 = vlan_data["parent_network"]
    parent_network2 = vlan_data["parent_network1"]
    parentport_name1 = vlan_data["parentport_name"]
    parentport_name2 = vlan_data["parentport_name1"]
    subport_network = vlan_data["subport_network"]
    subport_name1 = vlan_data["subport_name"]
    subport_name2 = vlan_data["subport_name1"]
    trunk_name = vlan_data["trunk_name"]
    flavor_name = vlan_data["static_flavor"]
    availability_zone = vlan_data["zone3"]
    image_name = vlan_data["static_image"]
    server_name1 = vlan_data["server_name"]
    server_name2 = vlan_data["server_name1"]
    security_group = vlan_data["static_secgroup"]
    segmentation_id = vlan_data["segmentation_id"]
    segmentation_type = vlan_data["segmentation_type"]
    old_eth_file_path = vlan_data["old_eth_file_path"]
    old_route_file_path = vlan_data["old_route_file_path"]
    gateway = vlan_data["gateway"]
    metricnumber = vlan_data["metricnumber"]
    key_file_path = vlan_data["key_file_path"]
    interface = "eth0.%s" % segmentation_id
    """1. ssh to director node.
        2. Create vlan-aware instance"vm-1" according the method given in test case above.
        3. Create another instance "vm-3" on the same network as the first instance. Dont create interfaces on this instance.
        4. ssh to vm-3
        5. ping the the vm-1's vlan-aware interface from the vm-3"""
    print("==========================================================================================================")
    print("====         VLAN AWARE VMS CASE 7:      verify flow of untagged traffic.                            =====")
    print("==========================================================================================================")
    try:
        network = creation_object.os_create_sriov_enabled_network(logger, conn_create,
                                                                  network_name=network_name,
                                                                  port_name=sriov_port,
                                        subnet_name=subnet_name, cidr=cidr, gateway=gateway,
                                        network_bool=True, subnet_bool=True, port_bool=True
                                        )
        # pdb.set_trace()
        router = creation_object.os_router_creation(logger, conn_create, router_name=router_name,
                                                     port_name=sriov_port, net_name=network_name)
        print("========             SERVER 1 CREATING WITH PARENT PORT                                =====")
        output = creation_object.os_create_vlan_aware_instance(logger, conn_create, parent_network=parent_network1,
                                                               parentport_name=parentport_name1,
                                                               subport_network=subport_network,
                                                               subport_name=subport_name1,
                                                               trunk_name=trunk_name,
                                                               flavor_name=flavor_name,
                                                               availability_zone=availability_zone,
                                                               image_name=image_name,
                                                               server_name=server_name1,
                                                               sec_group=security_group,
                                                               segmentation_id=segmentation_id,
                                                               segmentation_type=segmentation_type)

        pdb.set_trace()
        server_ip = output[2]
        subport_ip = output[3]
        ssh_obj.ssh_vlan_aware_vm(logger, server_ip, old_eth_file_path, new_eth_file_path, old_route_file_path,
                                  new_route_file_path, subport_ip, gateway, segmentation_id, metricnumber)
        ssh_obj.ssh_close()

        legacy = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name=dpdk_server,
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
# test_case1()
test_case3(delete_all=True)





