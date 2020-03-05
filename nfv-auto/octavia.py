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

f_ip=""
feature_name = "OCTAVIA"

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

def octavia_deployement_test_case_1(router_name,
                                                        network_name,subnet_name,
                                                        port_name,
                                                        server1_name,server2_name,
                                                        image_name,flavor_name,secgroup_name,
                                                        zone, cidr,gateway_ip,assign_floating_ip,
                                                        lb_name, listener_name, protocol, protocol_id, pool_name, algorithm,
                                                        member1_name, member2_name,
                                                        delete_all=False
                                                        ):
    global f_ip
    logger.info("f_ip value %s" %f_ip)
    logger.info("==========================================================================================================")
    logger.info("====         OCTAVIA TEST CASE 1:      CREATE A LOADBALANCER and Verify it By sending HTTP TRAFFIC.  =====")
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
    # #
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
            ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            ###-------------------------------------For Installing Fio-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            ssh_obj.execute_command_show_output(logger, "sudo yum install fio -y")
            ssh_obj.execute_command_show_output(logger, "sudo fio -v")
            ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            ssh_obj.execute_command_show_output(logger,"sudo sed -i '14 s/nginx/nginx %s VM %s/' /usr/share/nginx/html/index.html" %(ip_list[i], count))
            ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            count = count + 1
            ssh_obj.ssh_close()
        # # pdb.set_trace()
        logger.info("Loadbalancer creating..")
        os.system("openstack loadbalancer create --name %s --vip-subnet-id %s" % (lb_name,subnet_name))
        time.sleep (120)
        os.system("openstack loadbalancer show %s" % (lb_name))
        logger.info("Listener creating..")
        os.system("openstack loadbalancer listener create --name %s --protocol %s --protocol-port %s %s" % (listener_name, protocol, protocol_id, lb_name))
        time.sleep(5)
        logger.info("Pool creating..")
        os.system("openstack loadbalancer pool create --name %s --lb-algorithm %s --listener %s --protocol %s" % (pool_name, algorithm, listener_name, protocol))
        time.sleep(5)
        logger.info("Member1 creating..")
        os.system("openstack loadbalancer member create --name %s --subnet-id %s --address %s --protocol-port %s %s" % (member1_name, subnet_name, ip_list[1], protocol_id ,pool_name))
        time.sleep(5)
        logger.info("Member2 creating..")
        os.system("openstack loadbalancer member create --name %s --subnet-id %s --address %s --protocol-port %s %s" % (member2_name, subnet_name, ip_list[3], protocol_id ,pool_name))
        time.sleep(5)
        os.system("openstack loadbalancer list")
        os.system("openstack loadbalancer listener list")
        os.system("openstack loadbalancer pool list")
        os.system("openstack loadbalancer member list %s" % pool_name)
        #
        #
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


def octavia_deployement_test_case_2(router_name,
                                                        network_name,subnet_name,
                                                        port_name,
                                                        server1_name,server2_name,
                                                        image_name,flavor_name,secgroup_name,
                                                        zone, cidr,gateway_ip,assign_floating_ip,
                                                        lb_name, listener_name, protocol, protocol_id, pool_name, algorithm,
                                                        member1_name, member2_name,
                                                        delete_all=False
                                                        ):
    global f_ip
    logger.info("f_ip value %s" %f_ip)
    logger.info("==========================================================================================================")
    logger.info("====         OCTAVIA TEST CASE 2:      CREATE A LOADBALANCER For TCP Traffic.  =====")
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
    # #
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
        # for i in range(0,3,2):
            # logger.info("VM IP %s" % ip_list[i])
            # # ssh_obj.execute_command_show_output(logger, "sudo scp -rp -i dvr-key.pem nginx.repo centos@%s:./" %ip_list[i])
            # ssh_obj.ssh_to(logger, ip_list[i], data["static_image"], key_file_name=data["key_file_path"])
            # ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
            # ssh_obj.execute_command_show_output(logger, "sudo sed -i '/USERCTL=no/ a DNS1=8.8.8.8' /etc/sysconfig/network-scripts/ifcfg-eth0")
            # ssh_obj.execute_command_show_output(logger, "cat /etc/sysconfig/network-scripts/ifcfg-eth0")
            # ssh_obj.execute_command_show_output(logger, "sudo systemctl restart network")
            # ssh_obj.execute_command_show_output(logger, "ping -c 5 google.com")
            # ssh_obj.execute_command_show_output(logger, "ls")
            # ssh_obj.send_nginx_repo_if_not_present(logger, destination_path="./nginx.repo")
            # ssh_obj.execute_command_show_output(logger, "ls")
            # ssh_obj.execute_command_show_output(logger, "ls /etc/yum.repos.d/")
            # ssh_obj.execute_command_show_output(logger, "sudo cp ./nginx.repo /etc/yum.repos.d/")
            # ssh_obj.execute_command_show_output(logger, "ls /etc/yum.repos.d/")
            # # ssh_obj.send_file_or_package(logger, source_path="/home/osp_admin/NFV/nfv-auto/nginx.repo",
            # #                       destination_path="/etc/yum.repo.d/")
            # ssh_obj.execute_command_show_output(logger, "sudo yum-config-manager --enable nginx")
            # ssh_obj.execute_command_show_output(logger, "sudo yum install nginx -y")
            # ssh_obj.execute_command_show_output(logger, "sudo systemctl start nginx")
            # ssh_obj.execute_command_show_output(logger, "sudo systemctl status nginx")
            # ssh_obj.execute_command_show_output(logger, "sudo systemctl enable nginx")
            # ssh_obj.execute_command_show_output(logger, "sudo systemctl status nginx")
            # ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            # ###-------------------------------------For Installing Fio-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            # ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            # ssh_obj.execute_command_show_output(logger, "sudo yum install fio -y")
            # ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            # ###-------------------------------------==================-------------------------------------------------------%%%%%%%%%%%%%%%%%%%%%%
            # ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            # ssh_obj.execute_command_show_output(logger,"sudo sed -i '14 s/nginx/nginx %s VM %s/' /usr/share/nginx/html/index.html" %(ip_list[i], count))
            # ssh_obj.execute_command_show_output(logger, "sudo cat /usr/share/nginx/html/index.html")
            # count = count + 1
            # ssh_obj.ssh_close()
        # pdb.set_trace()
        logger.info("Loadbalancer creating..")
        os.system("openstack loadbalancer create --name %s --vip-subnet-id %s" % (lb_name,subnet_name))
        time.sleep (120)
        os.system("openstack loadbalancer show %s" % (lb_name))
        logger.info("Listener creating..")
        os.system("openstack loadbalancer listener create --name %s --protocol %s --protocol-port %s %s" % (listener_name, protocol, protocol_id, lb_name))
        time.sleep(5)
        logger.info("Pool creating..")
        os.system("openstack loadbalancer pool create --name %s --lb-algorithm %s --listener %s --protocol %s" % (pool_name, algorithm, listener_name, protocol))
        time.sleep(5)
        logger.info("Member1 creating..")
        os.system("openstack loadbalancer member create --name %s --subnet-id %s --address %s --protocol-port %s %s" % (member1_name, subnet_name, ip_list[1], protocol_id ,pool_name))
        time.sleep(5)
        logger.info("Member2 creating..")
        os.system("openstack loadbalancer member create --name %s --subnet-id %s --address %s --protocol-port %s %s" % (member2_name, subnet_name, ip_list[3], protocol_id ,pool_name))
        time.sleep(5)
        os.system("openstack loadbalancer list")
        os.system("openstack loadbalancer listener list")
        os.system("openstack loadbalancer pool list")
        os.system("openstack loadbalancer member list %s" % pool_name)
        #
        #
        floating_ip = creation_object.os_floating_ip_creation(logger, conn_create)
        f_ip=str(floating_ip['floating_ip_address'])
        lb_command="openstack loadbalancer listener show %s" % listener_name
        lb_data = ssh_obj.locally_execute_command(lb_command)
        # pdb.set_trace()
        logger.info(lb_data)
        out1 = str(lb_data.split("\n")[14].split("|")[2].strip())
        operating_status = str(out1)
        out2 = str(lb_data.split("\n")[18].split("|")[2].strip())
        provisioning_status = str(out2)

        res = "ONLINE && ACTIVE"

        if provisioning_status in res and operating_status in res:
            logger.info("Test Successful")
        else:
            logger.info("Test Failed")
        time.sleep(10)
        # pdb.set_trace()
        if delete_all:
            logger.info("Pool deleting..")
            os.system("openstack loadbalancer pool delete %s" % (pool_name))
            time.sleep(5)
            logger.info("Listener deleting..")
            os.system("openstack loadbalancer listener delete %s" % (listener_name))
            time.sleep(5)
        # lb_command="openstack loadbalancer show %s" % lb_name
        # lb_data = ssh_obj.locally_execute_command(lb_command)
        # logger.info(lb_data)
        # out = str(lb_data.split("\n")[18].split("|")[2].strip())
        # vip_port_id = str(out)
        # ssh_obj.locally_execute_command("openstack floating ip set --port %s %s"%(vip_port_id, f_ip))
        # os.system("openstack loadbalancer list")
        # logger.info("Testing LB working.......")
        # # os.system("for i in {1..6} ; do curl -w \"\n\" %s ; done" %f_ip)
        # res = ssh_obj.locally_execute_command("for i in {1..6} ; do curl -w \"\n\" %s ; done" %f_ip)
        # logger.info(res)
        # vm1_ip = ip_list[0]
        # vm2_ip = ip_list[2]
        # if vm1_ip in res and vm2_ip in res:
        #     logger.info("Test Successful")
        # else:
        #     logger.info("Test Failed")
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

def octavia_deployement_test_case_3(                    lb_name, listener_name, protocol, protocol_id, pool_name, algorithm,
                                                        delete_all=False
                                                        ):
    global f_ip
    logger.info("f_ip value %s" %f_ip)
    logger.info("==========================================================================================================")
    logger.info("====OCTAVIA TEST CASE 3:     CREATE A LISTENER For TCP Traffic ON LOADBALANCER USED IN TEST CASE 1.  =====")
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
    # #
    # exit()
    try:
        os.system("openstack loadbalancer show %s" % (lb_name))
        logger.info("Listener creating..")
        os.system("openstack loadbalancer listener create --name %s --protocol %s --protocol-port %s %s" % (listener_name, protocol, protocol_id, lb_name))
        time.sleep(5)
        logger.info("Pool creating..")
        os.system("openstack loadbalancer pool create --name %s --lb-algorithm %s --listener %s --protocol %s" % (pool_name, algorithm, listener_name, protocol))
        time.sleep(5)
        os.system("openstack loadbalancer list")
        os.system("openstack loadbalancer listener list")
        os.system("openstack loadbalancer pool list")
        os.system("openstack loadbalancer member list %s" % pool_name)
        #
        #
        lb_command="openstack loadbalancer listener show %s" % listener_name
        lb_data = ssh_obj.locally_execute_command(lb_command)
        # pdb.set_trace()
        logger.info(lb_data)
        out1 = str(lb_data.split("\n")[14].split("|")[2].strip())
        operating_status = str(out1)
        out2 = str(lb_data.split("\n")[18].split("|")[2].strip())
        provisioning_status = str(out2)

        res = "ONLINE && ACTIVE"

        if provisioning_status in res and operating_status in res:
            logger.info("Test Successful")
        else:
            logger.info("Test Failed")
        time.sleep(10)
        # pdb.set_trace()
        if delete_all:
            logger.info("Pool deleting..")
            os.system("openstack loadbalancer pool delete %s" % (pool_name))
            time.sleep(5)
            logger.info("Listener deleting..")
            os.system("openstack loadbalancer listener delete %s" % (listener_name))
            time.sleep(5)




        return ou1
    except:
            logger.info ("Unable to execute test case 1")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


            logger.info("Pool deleting..")
            os.system("openstack loadbalancer pool delete %s" % (pool_name))
            time.sleep(5)
            logger.info("Listener deleting..")
            os.system("openstack loadbalancer listener delete %s" % (listener_name))
            time.sleep(5)



server1_name = "octavia_vm1_http"
server2_name = "octavia_vm2_http"
network_name = "octavia-network-http"
subnet_name = "octavia-subnet-http"
router_name = "octavia-router"
port_name = "octavia-port-http"
zone = "nova0"
cidr = "192.168.70.0/24"
gateway_ip = "192.168.70.1"
flavor_name = "sanity_flavor"
image_name = "centos_7_signed"
secgroup_name = "69829dd9-e432-468b-beb7-e6fd6e67f7c8"
assign_floating_ip = True
#
lb_name="lb1_http"
listener_name="listener1_http"
protocol="HTTP"
protocol_id="80"
pool_name="pool1_http"
algorithm="ROUND_ROBIN"
member1_name="member1_http"
member2_name="member2_http"
#

# server1_name = "ceph-vm1"
# server2_name = "ceph-vm2"
# network_name = "ceph-net"
# subnet_name = "ceph-subnet"
# router_name = "ceph-router"
# port_name = "ceph-port-http"
# octavia_deployement_test_case_1(router_name=router_name,
#                                                         network_name=network_name,
#                                                         subnet_name=subnet_name,
#                                                         port_name=port_name,
#                                                         server1_name=server1_name,server2_name=server2_name,
#                                                         image_name=image_name,flavor_name=flavor_name,secgroup_name=secgroup_name,
#                                                         zone=zone, cidr=cidr,gateway_ip=gateway_ip,assign_floating_ip=assign_floating_ip,
#                                                         lb_name=lb_name,listener_name=listener_name, protocol=protocol, protocol_id=protocol_id,
#                                                         pool_name=pool_name, algorithm=algorithm, member1_name=member1_name, member2_name=member2_name,
#                                                         delete_all=False
#                                                         )
server1_name = "octavia_vm1_tcp"
server2_name = "octavia_vm2_ycp"
network_name = "octavia-network-tcp"
subnet_name = "octavia-subnet-tcp"
router_name = "octavia-router"
port_name = "octavia-port-tcp"
zone = "nova1"
cidr = "192.168.80.0/24"
gateway_ip = "192.168.80.1"
flavor_name = "sanity_flavor"
image_name = "centos_7_signed"
secgroup_name = "69829dd9-e432-468b-beb7-e6fd6e67f7c8"
assign_floating_ip = True

lb_name="lb1_tcp"
listener_name="listener1_tcp"
protocol="TCP"
protocol_id="23456"
pool_name="pool1_tcp"
algorithm="SOURCE_IP"
member1_name="member1_tcp"
member2_name="member2_tcp"
octavia_deployement_test_case_2(router_name=router_name,
                                                        network_name=network_name,
                                                        subnet_name=subnet_name,
                                                        port_name=port_name,
                                                        server1_name=server1_name,server2_name=server2_name,
                                                        image_name=image_name,flavor_name=flavor_name,secgroup_name=secgroup_name,
                                                        zone=zone, cidr=cidr,gateway_ip=gateway_ip,assign_floating_ip=assign_floating_ip,
                                                        lb_name=lb_name,listener_name=listener_name, protocol=protocol, protocol_id=protocol_id,
                                                        pool_name=pool_name, algorithm=algorithm, member1_name=member1_name, member2_name=member2_name,
                                                        delete_all=False
                                                        )

# lb_name="lb1_http"
# listener_name="listener2_tcp"
# protocol="TCP"
# protocol_id="23456"
# pool_name="pool2_tcp"
# algorithm="LEAST_CONNECTIONS"
# octavia_deployement_test_case_3(                    lb_name, listener_name, protocol, protocol_id, pool_name, algorithm,
#                                                         delete_all=False
#                                                         )
################################################################################################################
####################### NOT NEEDED==============================================================================
################################################################################################################
# def http_lb_session_persistence(lb_name,listener_name,protocol,protocol_id,pool_name,algorithm):
#     logger.info ("Creating http Load Balancer....")
#     os.system("openstack loadbalancer create --name %s --vip-subnet-id %s" %(lb_name,subnet_name))
#     time.sleep(1200)
#     logger.info("============================== Load Balancer ================================")
#     os.system("openstack loadbalancer show %s" %(lb_name))
#     logger.info ("Creating Listener....")
#     os.system("openstack loadbalancer listener create --name %s --protocol HTTP --protocol-port 80 %s " %(listener_name,lb_name))
#     logger.info ("Creating the Listener default pool....")
#     os.system("openstack loadbalancer pool create --name %s --lb-algorithm %s --listener %s --protocol % --session-persistence type=APP_COOKIE,cookie_name=PHPSESSIONID " %(pool_name,algorithm,listener_name,protocol_id))
################################################################################################################################################################################################################################
################################################################################################################################################################################################################################
########################################################
# def qos_ruled_lb_test_case_15(qos_policy_name,qos_type,lb_name,public_subnet,listener_name,protocol,pool_name,algorithm,private_subnet,instance1_address,instance2_address):
#     logger.info("Creating Policy...")
#     os.system("openstack network qos policy create %s" %qos_policy_name)
#     logger.info("Creating Rule...")
#     os.system("openstack network qos rule create --type %s --max-kbps 1024 --max-burst-kbits 1024 %s" %(qos_type,qos_policy_name))
#     logger.info("Creating Load Balancer...")
#     os.system("openstack loadbalancer create --name %s --vip-subnet-id %s --vip-qos-policy-id %s" %(lb_name,public_subnet,qos_policy_name))
#     time.sleep(120)
#     logger.info ("Creating Listener....")
#     os.system("openstack loadbalancer listener create --name %s --protocol %s --protocol-port 80 %s" %(listener_name,protocol,lb_name))
#     logger.info ("Creating LB Pool....")
#     os.system("openstack loadbalancer pool create --name %s --lb-algorithm %s --listener %s --protocol %s" %(pool_name,algorithm,listener_name,protocol))
#     logger.info ("Adding Instances to Pool....")
#     os.system("openstack loadbalancer member create --subnet-id %s --address %s --protocol-port 80 %s" %(private_subnet,instance1_address,pool_name))
#     os.system("openstack loadbalancer member create --subnet-id %s --address %s --protocol-port 80 %s" %(private_subnet, instance2_address, pool_name))

###############################################################################
# def create_loadbalancer_L7_policy_test_case_16(listener_name,protocol,protocol_id,lb_name,redirect_url,l7policy_name,action_url):
#     logger.info("Creating Listener....")
#     os.system("openstack loadbalancer listener create --name %s --protocol %s --protocol-port %s %s" %(listener_name,protocol,protocol_id,lb_name))
#     time.sleep(120)
#     logger.info("Creating l7policy....")
#     os.system("openstack loadbalancer l7policy create --action %s --redirect-url %s --name %s %s" %(action_url,redirect_url,l7policy_name,listener_name))
#     logger.info("Creating l7rule....")
#     os.system("openstack loadbalancer l7rule create --compare-type STARTS_WITH --type PATH --value / %s" %l7policy_name)
############################################################################
# def create_static_pool_with_previous_listener_and_create_L7_policy_test_17(algorithm,lb_name,pool_name,protocol,private_subnet,instance1_address,instance2_address,l7policy_name,listener_name,l7policy_name2,action_url):
#     logger.info("Creating Pool....")
#     os.system("openstack loadbalancer pool create --lb-algorithm %s --loadbalancer %s --name %s --protocol %s" %(algorithm,lb_name,pool_name,protocol))
#     logger.info("Creating two members....")
#     os.system("openstack loadbalancer member create --subnet-id %s --address %s --protocol-port %s %s" %(private_subnet, instance1_address,protocol_id, pool_name))
#     os.system("openstack loadbalancer member create --subnet-id %s --address %s --protocol-port %s %s" %(private_subnet, instance2_address,protocol_id, pool_name))
#     logger.info("Creating L7 Policy policy1 with action.....")
#     os.system("openstack loadbalancer l7policy create --action %s --redirect-pool %s --name %s %s" %(action_url,pool_name,l7policy_name,listener_name))
#     logger.info("Creating L7 Policy policy2 with action.....")
####################################################################################################
#
# qos_policy_name="qos-policy-bandwidth"
# qos_type="bandwidth_limit"
# public_subnet="public-subnet"
# private_subnet="private-subnet"
# instance1_address="192.168.10.11"
# instance2_address="192.168.10.12"
# l7policy_name="policy1"
# l7policy_name2="policy2"
# redirect_url="https://www.example.com/"
# action_url="google.com"




###################################
# qos_ruled_lb_test_case_15(qos_policy_name,qos_type,lb_name,public_subnet,listener_name,protocol,pool_name,algorithm,private_subnet,instance1_address,instance2_address)