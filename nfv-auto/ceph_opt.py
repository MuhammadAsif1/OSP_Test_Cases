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

feature_name = "Ceph Optimization Script"

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

def execute_tcp_dump(session, timeout, namespace_id ,interface, find=None):
    global stdout_a
    try:
        #print "\nExecuting tcp dump command to capture PAD packets"
        if find is None:
            stdin_a, stdout_a, stderr_a = session.exec_command("sudo ip netns exec %s timeout %s tcpdump -i %s" %
                                                               (namespace_id, timeout, interface))
        else:
            stdin_a, stdout_a, stderr_a = session.exec_command("sudo ip netns exec %s timeout %s tcpdump -i %s | grep '%s'" %
                                                               (namespace_id, timeout, interface, find))
    except:
        logger.info ("\nError while executing tcp dump command")

command_proc_id_of_l3_agent = "sudo docker ps | grep neutron_l3_agent"

command_sudo_ifconfig = "sudo ifconfig"

# def create_connection(flag):
#     if flag == "create":
#         connect = creation_object.os_connection_creation()
#     elif flag == "delete":
#         connect = delete_object.os_connection_creation()
#     else:
#         logger.info ("Identify flag.. Create or Delete!")
#     if connect:
#         logger.info("Connection Build Successfully for %s" % flag)
#     else:
#         logger.info("Connecion Failed %s" % flag)
#     return connect

def ceph_vm_setup(router_name,
                                                        network_name,subnet_name,
                                                        port_name,
                                                        server_name,
                                                        server_count,
                                                        image_name,flavor_name,secgroup_name,
                                                        zone,
                                                        cidr,gateway_ip,assign_floating_ip,
                                                        delete_all=False
                                                        ):
    logger.info("==========================================================================================================")
    logger.info("====         CEPH ENVIRONMENT SETUP:      CREATE VM'S FOR COMPUTE NODE 0.                            =====")
    logger.info("==========================================================================================================")
    # logger.info("Pool deleting..")
    # os.system("openstack loadbalancer pool delete %s" % (pool_name))
    # logger.info("Listener deleting..")
    # os.system("openstack loadbalancer listener delete %s" % (listener_name))
    # logger.info("Loadbalancer deleting..")
    # logger.info("Loadbalancer deleted Successfully")
    # os.system("openstack loadbalancer delete %s" % (lb_name))
    # pdb.set_trace()
    # router = conn_create.get_router(name_or_id=router_name, filters=None)
    # delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete,
    #                                                            server1_name, server2_name,
    #                                                            network_name,
    #                                                            router_name, port_name)
    #
    # exit()
    # def create_1_instances_on_same_compute_same_network(self, logger, conn, server_name, network_name, subnet_name,
    #                                                     router_name, port_name, zone, cidr,
    #                                                     gateway_ip, flavor_name, image_name,
    #                                                     secgroup_name, assign_floating_ip):
    i = 1
    j = 2
    nova0_list=[]
    nova1_list=[]
    nova2_list=[]
    # volume_name = "%s_vol_1" %server_name
    try:
        while j < 3:
            while i < server_count:
                servr_name = "%s_%s_nova_%s" % (server_name, i, j)
                if j==0:
                    zone = "nova0"

                if j==1:
                    zone = "nova1"

                if j==2:
                    zone = "nova2"
                ip_list  = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create,
                                                                                           servr_name, network_name,
                                                                subnet_name,
                                                                router_name, port_name, zone, cidr,
                                                                gateway_ip, flavor_name, image_name,
                                                                secgroup_name, assign_floating_ip)
                logger.info("output %s" % ip_list)#Nid,Rid,Sid,Pip,Fip

                ###########Creating and Attaching Volume to VM#############################
                # os.system("openstack volume create --size 40 %s" % volume_name)
                # creation_object.os_attach_volume(logger, conn_create, server_name, volume_name)
                time.sleep(50)

                ###### Installing FIO in VM ##########
                count = 1
                logger.info("VM IP %s" % ip_list[4])
                if j==0:
                    nova0_list.append(ip_list[4])

                if j==1:
                    nova1_list.append(ip_list[4])

                if j==2:
                    nova2_list.append(ip_list[4])
                # pdb.set_trace()
                # ssh_obj.execute_command_show_output(logger, "sudo scp -rp -i dvr-key.pem nginx.repo centos@%s:./" %ip_list[i])
                ssh_obj.ssh_to(logger, ip_list[4], username=data["static_image"], key_file_name=data["key_file_path"])
                ssh_obj.execute_command_show_output(logger, "ls")
                ssh_obj.execute_command_show_output(logger, "ifconfig")
                ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
                ssh_obj.execute_command_show_output(logger, "sudo sed -i '/USERCTL=no/ a DNS1=8.8.8.8' /etc/sysconfig/network-scripts/ifcfg-eth0")
                ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
                ssh_obj.execute_command_show_output(logger, "sudo systemctl restart network")
                ssh_obj.execute_command_show_output(logger, "ping -c 5 google.com")
                ssh_obj.execute_command_show_output(logger, "ls")
                ssh_obj.execute_command_show_output(logger, "sudo yum install fio -y")
                res = ssh_obj.execute_command_show_output(logger, "sudo fio -v")
                # count = count + 1
                ssh_obj.ssh_close()
                # # pdb.set_trace()
                # logger.info(count)
                # vm_p_ip = ip_list[3]
                # vm_f_ip = ip_list[4]
                # if res != None:
                #     logger.info("FIO installed on %s Successful" %server_name)
                # else:
                #     logger.info("FIO installed on %s Failed" % server_name)
                # time.sleep(10)
                # pdb.set_trace()
                logger.info("VM CREATED SUCCESSFULLY")
                if delete_all:
                    delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete,
                                                                           server_name,
                                                                           network_name,
                                                                           router_name, port_name)

                i = i + 1
                logger.info("%s" % nova0_list)
                logger.info("%s" % nova1_list)
                logger.info("%s" % nova2_list)
            j = j + 1

    except:
            logger.info ("Unable to execute test case 1")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
            delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete,
                                                                   server_name,
                                                                   network_name,
                                                                   router_name, port_name)

    return nova2_list

server_name = "ceph_vm"
server_count = 3
network_name = "storage-net"
subnet_name = "storage-subnet"
router_name = "storage-router"
port_name = "storage-port"
zone0 = "nova0"
zone1 = "nova1"
zone2 = "nova2"
cidr = "192.168.70.0/24"
gateway_ip = "192.168.70.1"
flavor_name = "m1.medium"
image_name = "centos"
secgroup_name = "c11a0ebb-22bb-4658-9804-c20d0053412a"
assign_floating_ip = True


# def ceph_vm_setup(router_name,
#                                                         network_name,subnet_name,
#                                                         port_name,
#                                                         server_name,
#                                                         server_count,
#                                                         image_name,flavor_name,secgroup_name,
#                                                         zone,
#                                                         cidr,gateway_ip,assign_floating_ip,
#                                                         delete_all=False
#                                                         ):

ceph_vm_setup(router_name=router_name,
                    network_name=network_name,
                    subnet_name=subnet_name,
                    port_name=port_name,
                    server_name=server_name,server_count=server_count,
                    image_name=image_name,flavor_name=flavor_name,secgroup_name=secgroup_name,
                    zone=zone0,
                    cidr=cidr,gateway_ip=gateway_ip,
                    assign_floating_ip=assign_floating_ip,
                    delete_all=False
                                                        )