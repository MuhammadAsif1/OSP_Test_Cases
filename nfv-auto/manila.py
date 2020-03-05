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

feature_name = "MANILA WITH UNITY"

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

def manila_deployement_test_case_1(router_name,
                                                        network_name,subnet_name,
                                                        port_name,
                                                        server1_name,server2_name,
                                                        image_name,flavor_name,secgroup_name,
                                                        zone, cidr,gateway_ip,assign_floating_ip,
                                                        lb_name, listener_name, protocol, protocol_id, pool_name, algorithm,
                                                        member1_name, member2_name,
                                                        delete_all=False
                                                        ):
    logger.info("====================================================================================================================")
    logger.info("==== MANILA TEST CASE 1:   CREATE NETWORK STACK WITH 2 VM's & Also Create MANILA STACK & VERIFY IT'S WORKING.  =====")
    logger.info("====================================================================================================================")
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
    try:
        ip_list  = creation_object.create_2_instances_on_same_compute_same_network(logger, conn_create, server1_name, server2_name, network_name,
                                                        subnet_name,
                                                        router_name, port_name, zone, cidr,
                                                        gateway_ip, flavor_name, image_name,
                                                        secgroup_name, assign_floating_ip)
        logger.info("output %s" % ip_list)#f1,p1,f2,p2
        # pdb.set_trace()

        ###### Installing nginx in VM ##########
        count = 1
        for i in range(0,3,2):
            logger.info("VM IP %s" % ip_list[i])
            # ssh_obj.execute_command_show_output(logger, "sudo scp -rp -i dvr-key.pem nginx.repo centos@%s:./" %ip_list[i])
            ssh_obj.ssh_to(logger, ip_list[i], data["static_image"], key_file_name=data["key_file_path"])
            ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
            ssh_obj.execute_command_show_output(logger, "sudo sed -i '/USERCTL=no/ a DNS1=8.8.8.8' /etc/sysconfig/network-scripts/ifcfg-eth0")
            ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
            ssh_obj.execute_command_show_output(logger, "sudo systemctl restart network")
            ssh_obj.execute_command_show_output(logger, "ping -c 5 google.com")
            ssh_obj.execute_command_show_output(logger, "ls")
            ssh_obj.send_nginx_repo_if_not_present(logger, destination_path="./nginx.repo")
            ssh_obj.execute_command_show_output(logger, "ls")
            ssh_obj.execute_command_show_output(logger, "ls /etc/yum.repos.d/")
            ssh_obj.execute_command_show_output(logger, "sudo cp ./nginx.repo /etc/yum.repos.d/")
            ssh_obj.execute_command_show_output(logger, "ls /etc/yum.repos.d/")
            # ssh_obj.send_file_or_package(logger, source_path="/home/osp_admin/NFV/nfv-auto/nginx.repo",
            #                       destination_path="/etc/yum.repo.d/")
            ssh_obj.execute_command_show_output(logger, "sudo yum-config-manager --enable nginx")
            ssh_obj.execute_command_show_output(logger, "sudo yum install nginx -y")
            ssh_obj.execute_command_show_output(logger, "sudo systemctl start nginx")
            ssh_obj.execute_command_show_output(logger, "sudo systemctl status nginx")
            ssh_obj.execute_command_show_output(logger, "sudo systemctl enable nginx")
            ssh_obj.execute_command_show_output(logger, "sudo systemctl status nginx")

            ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            ssh_obj.execute_command_show_output(logger,"sudo sed -i '14 s/nginx/nginx %s VM %s/' /usr/share/nginx/html/index.html" %(ip_list[i], count))
            ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            count = count + 1
            ssh_obj.ssh_close()
        # pdb.set_trace()
        logger.info("Creating NFS Share..")
        os.system("manila create --name share-1 --share-type unity_share --share-network unity_share_net nfs 10")
        time.sleep (5)
        logger.info("Verify Share Creation..")
        os.system("manila list")
        logger.info("Note:  Manila Share Export Location...")
        os.system("manila share-export-location-list share-1")
        time.sleep(5)
        logger.info("Allow VM 1 To Access Share...")
        os.system("manila access-allow share-1 ip %s" %ip_list[0])
        time.sleep(5)
        logger.info("Verify That VM 1 is Allowed To Access Share..")
        os.system("manila access-list share-1")
        time.sleep(5)
        logger.info("Member2 creating..")
        os.system("openstack loadbalancer member create --name %s --subnet-id %s --address %s --protocol-port %s %s" % (member2_name, subnet_name, ip_list[3], protocol_id ,pool_name))
        time.sleep(5)
        os.system("openstack loadbalancer list")
        os.system("openstack loadbalancer listener list")
        os.system("openstack loadbalancer pool list")
        os.system("openstack loadbalancer member list %s" % pool_name)


        floating_ip = creation_object.os_floating_ip_creation(logger, conn_create)
        f_ip=str(floating_ip['floating_ip_address'])
        lb_command="openstack loadbalancer show %s" % lb_name
        lb_data = ssh_obj.locally_execute_command(lb_command)
        logger.info(lb_data)
        out = str(lb_data.split("\n")[18].split("|")[2].strip())
        vip_port_id = str(out)
        ssh_obj.locally_execute_command("openstack floating ip set --port %s %s"%(vip_port_id, f_ip))
        os.system("openstack loadbalancer list")
        logger.info("Testing LB working.......")
        # os.system("for i in {1..6} ; do curl -w \"\n\" %s ; done" %f_ip)
        res = ssh_obj.locally_execute_command("for i in {1..6} ; do curl -w \"\n\" %s ; done" %f_ip)
        logger.info(res)
        vm1_ip = ip_list[0]
        vm2_ip = ip_list[2]
        if vm1_ip in res and vm2_ip in res:
            logger.info("Test Successful")
        else:
            logger.info("Test Failed")
        time.sleep(10)
        # pdb.set_trace()
        if delete_all:
            logger.info("member1 deleting..")
            os.system("openstack loadbalancer member delete %s %s" % (pool_name, member1_name))
            time.sleep(5)
            logger.info("member2 deleting..")
            os.system("openstack loadbalancer member delete %s %s" % (pool_name, member2_name))
            time.sleep(5)
            logger.info("Pool deleting..")
            os.system("openstack loadbalancer pool delete %s" % (pool_name))
            time.sleep(5)
            logger.info("Listener deleting..")
            os.system("openstack loadbalancer listener delete %s" % (listener_name))
            time.sleep(5)
            logger.info("Loadbalancer deleting..")
            os.system("openstack loadbalancer delete %s" % (lb_name))
            time.sleep(5)
            logger.info("Loadbalancer deleted Successfully")
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete,
                                                                   server1_name, server2_name,
                                                                   network_name,
                                                                   router_name, port_name)


        return ip_list
    except:
            logger.info ("Unable to execute test case 1")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

            logger.info("member1 deleting..")
            os.system("openstack loadbalancer member delete %s %s" % (pool_name, member1_name))
            time.sleep(5)
            logger.info("member2 deleting..")
            os.system("openstack loadbalancer member delete %s %s" % (pool_name, member2_name))
            time.sleep(5)
            logger.info("Pool deleting..")
            os.system("openstack loadbalancer pool delete %s" % (pool_name))
            time.sleep(5)
            logger.info("Listener deleting..")
            os.system("openstack loadbalancer listener delete %s" % (listener_name))
            time.sleep(5)
            logger.info("Loadbalancer deleting..")
            os.system("openstack loadbalancer delete %s" % (lb_name))
            time.sleep(5)
            logger.info("Loadbalancer deleted Successfully")
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete,
                                                                       server1_name, server2_name,
                                                                       network_name,
                                                                       router_name, port_name)



server1_name = "manila-vm1"
server2_name = "manila-vm2"
network_name = "manila-network"
subnet_name = "manila-subnet"
router_name = "manila-router"
port_name = "manila-port"
zone = "nova1"
cidr = "192.168.70.0/24"
gateway_ip = "192.168.70.1"
flavor_name = "sanity_flavor"
image_name = "centos"
secgroup_name = "5ffacd02-d1a0-4682-abf3-b427f0c61831"
assign_floating_ip = True

unity_network_server_ip="192.168.170.221"

lb_name="lb1"
listener_name="listener1"
protocol="HTTP"
protocol_id="80"
pool_name="pool1"
algorithm="ROUND_ROBIN"
member1_name="vm1_member"
member2_name="vm2_member"

manila_deployement_test_case_1(router_name=router_name,
                                                        network_name=network_name,
                                                        subnet_name=subnet_name,
                                                        port_name=port_name,
                                                        server1_name=server1_name,server2_name=server2_name,
                                                        image_name=image_name,flavor_name=flavor_name,secgroup_name=secgroup_name,
                                                        zone=zone, cidr=cidr,gateway_ip=gateway_ip,assign_floating_ip=assign_floating_ip,
                                                        lb_name=lb_name,listener_name=listener_name, protocol=protocol, protocol_id=protocol_id,
                                                        pool_name=pool_name, algorithm=algorithm, member1_name=member1_name, member2_name=member2_name,
                                                        delete_all=True
                                                        )