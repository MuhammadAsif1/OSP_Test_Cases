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

feature_name = "DVR"

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

def dvr_deployement_test_case_4(controller_ip_list, username):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 1:      Verify that DVR is deployed on all the controller nodes.          =====")
    logger.info("==========================================================================================================")
    try:
        logger.info ("Controller ip's %s" % controller_ip_list)
        for control in controller_ip_list:
            ssh_obj.ssh_to(logger, control,username)
            logger.info("Test running for controller- %s" %control)
            res = ssh_obj.execute_command_return_output(logger, command_proc_id_of_l3_agent)
            out = res.split("\n")
            l3_agent_id_control = str(out[0].split(" ")[0])
            res = ssh_obj.execute_command_return_output(logger, "sudo docker exec -t %s cat /etc/neutron/l3_agent.ini | grep \"agent_mode\"" %l3_agent_id_control)
            logger.info (res)
            if "agent_mode=dvr_snat" in str(res.split("\n")):
                logger.info ("TEST SUCCESSFUL")
                ssh_obj.ssh_close()
            else:
                logger.info ("TEST FAILED")
                ssh_obj.ssh_close()
        return res
    except:
            logger.info ("Unable to execute test case 1")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_5(compute_ip_list,username):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 2:     Verify that DVR is deployed on all the compute nodes.              =====")
    logger.info("==========================================================================================================")
    try:
        logger.info ("Compute ip's %s" % compute_ip_list)
        for comp in compute_ip_list:
            logger.info ("Test running for compute- %s" % comp)
            ssh_obj.ssh_to(logger, comp,username)
            res = ssh_obj.execute_command_return_output(logger, command_proc_id_of_l3_agent)
            out = res.split("\n")
            l3_agent_id_compute = str(out[0].split(" ")[0])
            res = ssh_obj.execute_command_return_output(logger, "sudo docker exec -t %s cat /etc/neutron/l3_agent.ini | grep \"agent_mode\"" %l3_agent_id_compute)
            logger.info(res)
            if "agent_mode=dvr" in str(res.split("\n")):
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

# def dvr_deployement_test_case_6(compute_ip,username,server_name):#################SKIP##############
#     logger.info("==========================================================================================================")
#     logger.info("====         DVR TEST CASE :            Validate the creation of bond2                              =====")
#     logger.info("====                                 its HA in DVR deployed with 7 ports.                            =====")
#     logger.info("==========================================================================================================")
#     try:
#         global float_ip
#         res = None
#         network_name = "last"
#         flavor_name = "last"
#         image_name = "last"
#         secgroup_name = "last"
#         # =====================================================================================================================
#         ssh_obj.ssh_to(logger, compute_ip, username)
#         # res = ssh_obj.execute_command_return_output(logger, "sudo ifconfig | grep \"flags=\"")
#         res = ssh_obj.check_interface_names(logger, )
#         logger.info (res)
#         ssh_obj.ssh_close()
#         # pdb.set_trace()
#         # availability_zone=creation_object.os_create_aggregate_and_add_host(conn_create, name, availablity_zone, host_name)
#         # =====================================================================================================================
#
#         vm = creation_object.os_server_creation(conn_create, server_name, flavor_name, image_name, network_name, secgroup_name, availability_zone="sriov-zone")
#         float_ip = creation_object.os_floating_ip_creation_assignment(conn_create, server_name)
#         logger.info (float_ip)
#         ip = str(float_ip.floating_ip_address)
#         logger.info (ip)
#         time.sleep(10)
#         #pdb.set_trace()
#
#         #=====================================================PSEUDO CODE=====================================================
#         # ssh_obj.ssh_to(logger, compute_ip, username)
#         # res = ssh_obj.execute_command_return_output(logger, "sudo ifdown <interface of bond2>")
#         # logger.info res
#         # ssh_obj.ssh_close()
#         #=====================================================================================================================
#         res = ssh_obj.locally_ping_check(logger, ip)
#         if res:
#             logger.info ("TEST SUCCESSFUL")
#         else:
#             logger.info ("TEST FAILED")
#         pdb.set_trace()
#
#         delete_object.os_delete_server(logger, conn_delete, server_name)
#         return res
#     except:
#         logger.info ("Unable to execute test case 6")
#         logger.info ("\nError: " + str(sys.exc_info()[0]))
#         logger.info ("Cause: " + str(sys.exc_info()[1]))
#         logger.info ("Line No: %s \n" %(sys.exc_info()[2].tb_lineno))
#
#         delete_object.os_delete_server(logger, conn_delete, server_name)
#         if res != None:
#             return res
#         else:
#             logger.info ("TEST FAILED")
#             return None

def dvr_deployement_test_case_10():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 3:     Verify that L3 agent must be distributed on all the compute nodes. =====")
    logger.info("==========================================================================================================")
    try:

        # out
        count = 0
        res1 = ssh_obj.locally_execute_command("openstack network agent list --agent-type l3")
        for i in range(3,9):
         out = str(res1.split("\n")[i].split("|")[3].strip())
         if "controller-0" in out or "controller-1" in out or "controller-2" in out or "compute-0" in out or "compute-1" in out or "compute-2" in out:
            logger.info ("%s found"%out)
            count += 1
         else:
            logger.info ("Test Failed")
            break
        if count == 6:
         logger.info ("TEST SUCCESSFUL")

        return out
    except:
        logger.info ("Unable to execute test case 3")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_11(controller_ip,username,router_name,
                                                        network1_name,network2_name,
                                                        subnet1_name,subnet2_name,
                                                        port1_name,port2_name,
                                                        server1_name,server2_name,
                                                        image_name,flavor_name,secgroup_name,
                                                        zone1,zone2, cidr1,gateway_ip1,
                                                        cidr2, gateway_ip2):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 4:     Verify traffic between 2 Compute nodes bypasses Controller node.   =====")
    logger.info("==========================================================================================================")
    try:
        interface_name_tc11 = "qr"

        ip_list = creation_object.create_2_instances_on_dif_compute_dif_network(logger, conn_create, server1_name, server2_name,
                                                                                network1_name, network2_name,
                                                                                subnet1_name, subnet2_name,
                                                                                router_name,
                                                                                port1_name,port2_name,
                                                                                zone1, zone2,
                                                                                cidr1,gateway_ip1,
                                                                                cidr2, gateway_ip2,
                                                                                flavor_name, image_name,
                                                                                secgroup_name,
                                                                                assign_floating_ip=True)
        logger.info (ip_list)
        time.sleep(50)
        router_id = conn_create.get_router(
						router_name
						).id
        logger.info (router_id)
        namespace_id = "qrouter-%s"%str(router_id)
        logger.info (namespace_id)
        ssh_obj.ssh_to(logger, controller_ip, "heat-admin")
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns exec %s ip a | grep %s" %(namespace_id, interface_name_tc11))#tap is not a desire interface this will be changed according to the test case designed which is qr-
        # pdb.set_trace()
        out = res.split("\n")
        interface_list = []
        for line in out:
            if "qr" in str(line):
                try:
                    int_f = line.split(":")[1].strip()
                    logger.info (int_f)
                    interface_list.append(int_f)
                except:
                    pass
        logger.info (interface_list)
        ssh_obj.ssh_close()
        count = 0
        for interface in interface_list:
            ssh_obj.ssh_to(logger, ip_list[0], data["static_image"], key_file_name=data["key_file_path"])
            ssh_2 = ssh_obj.start_second_session()
            ssh_2.connect(hostname=controller_ip, username="heat-admin")
            tcpres = execute_tcp_dump(session=ssh_2, timeout=30, namespace_id=namespace_id, interface=interface)
            res = ssh_obj.simple_ping_check(logger, ip_list[3])
            logger.info (res)
            ssh_obj.ssh_close()
            res1 = str(stdout_a.read())
            ssh_2.close()
            logger.info(tcpres)
            logger.info (res1)

            ######## check the ping packets in the tcpdump result shown=====================================================
            logger.info (res1)
            time.sleep(5)
            if ip_list[3] not in res1 and ip_list[0] not in res1:
                logger.info("TEST SUCCESSFUL for interface %s"%interface)
                count += 1
            else:
                logger.info("TEST FAILED for interface %s"%interface)

        ssh_obj.ssh_close()

        if count > 0:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete,
                                                                    server1_name, server2_name,
                                                                    network1_name, network2_name,
                                                                    router_name,
                                                                    port1_name, port2_name)

        return res1
    except:
            logger.info ("Unable to execute test case 4")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" %(sys.exc_info()[2].tb_lineno))

            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                        network1_name, network2_name,
                                                                        router_name,
                                                                        port1_name, port2_name)

def dvr_deployement_test_case_12(controller_ip_list, username, network_name, subnet_name, router_name, port_name, server_name,
                                 image_name, flavor_name, secgroup_name, zone, cidr, gateway_ip):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 5:     Verify the snat traffic transverse through the controller node.    =====")
    logger.info("==========================================================================================================")
    try:
        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
        #                                                           router_name, port_name)
        #pdb.set_trace()
        #server = creation_object.os_server_creation(conn_create, server_name, flavor_name, image_name, network_name, secgroup_name, availability_zone=zone)
        #[network_id, router_id, server_id, str(server_ip), str(f_ip_munch.floating_ip_address)]

        list_return = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name, network_name, subnet_name,
                                                      router_name, port_name, zone, cidr,
                                                      gateway_ip, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip=False)
        time.sleep(30)
        network_id = conn_create.get_network(network_name).id
        router_id = conn_create.get_router(router_name).id
        namespace_id = "qdhcp-%s"%str(network_id)
        interface_name_tc12 = "sg"
        snat_namespace_id = "snat-%s"%str(router_id)#################check and asked for snat_namespace_id
        logger.info (list_return)
        logger.info (network_id)
        logger.info (namespace_id)
        logger.info (router_id)
        private_ip = list_return[3]
        control_ip = None
        logger.info("List of controller ip's %s" % controller_ip_list)
        # pdb.set_trace()
        for controller_ip in controller_ip_list:
            ssh_obj.ssh_to(logger, controller_ip, username)
            res1 = ssh_obj.execute_command_return_output(logger, "sudo ip netns")
            if snat_namespace_id in res1:
                control_ip = controller_ip
                ssh_obj.ssh_close()
                break
            else:
                logger.info ("snat namespace not found in controller %s"%controller_ip)
                ssh_obj.ssh_close()
        # pdb.set_trace()
        ssh_obj.ssh_to(logger, control_ip, username)
        ssh_obj.send_key_if_not_present(logger, destination_path="/home/heat-admin/ssh-key.pem")
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns exec %s ip a | grep %s" %
                                                    (snat_namespace_id, interface_name_tc12))
        out = res.split("\n")
        interface_list = []
        for line in out:
            if "sg" in str(line):
                try:
                    int_f = line.split(":")[1].strip()
                    logger.info (int_f)
                    interface_list.append(int_f)
                except:
                    pass
        logger.info (interface_list)
        count = 0
        #pdb.set_trace()
        for interface in interface_list:
            ssh_2 = ssh_obj.start_second_session()
            ssh_2.connect(hostname=control_ip, username=username)
            tcpres = execute_tcp_dump(session=ssh_2, timeout=30, namespace_id=snat_namespace_id, interface=interface)
            check = ssh_obj.ping_check_from_namespace(logger, namespace_id=namespace_id, ip_of_instance1=private_ip,
                                                      username_of_instance="centos",
                                                      key_file_path_of_node="/home/heat-admin/ssh-key.pem",
                                                      ip_of_instance2="8.8.8.8")

            res1 = str(stdout_a.read())
            logger.info(tcpres)
            logger.info(check)
            ssh_2.close()
            logger.info (res1)
            if "google-public-dns-a.google.com > %s"%private_ip in res1 and "%s > google-public-dns-a.google.com"%private_ip in res1 or "dns.google > %s"%private_ip in res1 and "%s > dns.google"%private_ip in res1:
                logger.info("TEST SUCCESSFUL for interface %s" % interface)
                count += 1
            else:
                logger.info("TEST FAILED for interface %s" % interface)

        ssh_obj.ssh_close()

        if count > 0 :
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

        return res1
    except:
        logger.info ("Unable to execute test case 5")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

def dvr_deployement_test_case_13(controller_ip_list, username, network_name, subnet_name, router_name, port_name, server_name,
                                 image_name, flavor_name, secgroup_name, zone, cidr, gateway_ip):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 6:         Verify traffic with floatingIPs                                =====")
    logger.info("====                          for external traffic bypass Controller node.                           =====")
    logger.info("==========================================================================================================")

    try:
        # pdb.set_trace()
        # server = creation_object.os_server_creation_with_floating_ip(conn_create, server_name, flavor_name, image_name,
        #                                                              network_name, secgroup_name, availability_zone=zone,
        #                                                              assign_floating_ip=assign_floating_ip)
        # [network_id, router_id, server_id, str(server_ip), str(f_ip_munch.floating_ip_address)]
        list_return = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name,
                                                                                      network_name, subnet_name,
                                                                                      router_name, port_name, zone,
                                                                                      cidr,
                                                                                      gateway_ip, flavor_name,
                                                                                      image_name,
                                                                                      secgroup_name,
                                                                                      assign_floating_ip=True)
        ##################============   check for qg-interface and qr-namespace
        router_id = conn_create.get_router(
            router_name
        ).id
        network_id = conn_create.get_network(
            network_name
        ).id

        interface_name_tc13 = "qr"
        qr_namespace_id = "qrouter-%s" % str(router_id)
        logger.info (list_return)
        logger.info (router_id)
        # pdb.set_trace()
        # delete_object.os_delete_server(logger, conn_delete,server_name)
        private_ip = list_return[3]
        floating_ip = list_return[4]
        time.sleep(40)
        # float_ip = creation_object.os_floating_ip_creation_assignment(conn_create, server_name)  ##punlic network must be reviewed
        # ssh_obj.ssh_with_key(ip=floating_ip, username="centos", key_file_name="~/key.pem")
        # pdb.set_trace()
        control_ip = None
        for controller_ip in controller_ip_list:
            ssh_obj.ssh_to(logger, controller_ip, username)
            res1 = ssh_obj.execute_command_return_output(logger, "sudo ip netns")
            if qr_namespace_id in res1:
                control_ip = controller_ip
                ssh_obj.ssh_close()
                break
            else:
                logger.info ("qr namespace not found in controller %s"%controller_ip)
                ssh_obj.ssh_close()

        logger.info (control_ip)
        ssh_obj.ssh_to(logger, control_ip, username)
        ssh_obj.send_key_if_not_present(logger, destination_path="/home/heat-admin/ssh-key.pem")
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns exec %s ip a | grep %s" %
                                                    (qr_namespace_id, interface_name_tc13))
        out = res.split("\n")
        interface_list = []
        for line in out:
            if interface_name_tc13 in str(line):
                try:
                    int_f = line.split(":")[1].strip()
                    logger.info (int_f)
                    interface_list.append(int_f)
                except:
                    pass
        logger.info (interface_list)
        ssh_obj.ssh_close()
        count = 0
        # pdb.set_trace()
        for interface in interface_list:
            ssh_obj.ssh_to(logger, floating_ip, data["static_image"], key_file_name=data["key_file_path"])
            ssh_2 = ssh_obj.start_second_session()
            ssh_2.connect(hostname=controller_ip, username="heat-admin")
            tcpres = execute_tcp_dump(session=ssh_2, timeout=30, namespace_id=qr_namespace_id, interface=interface)
            res = ssh_obj.simple_ping_check(logger, "8.8.8.8")
            logger.info (res)
            res1 = str(stdout_a.read())
            ssh_obj.ssh_close()
            logger.info(tcpres)
            ssh_2.close()
            logger.info (res1)
            if "google-public-dns-a.google.com > %s" % private_ip not in res1 and "%s > google-public-dns-a.google.com" % private_ip not in res1:
                logger.info("TEST SUCCESSFUL for interface %s" % interface)
                count += 1
            else:
                logger.info("TEST FAILED for interface %s" % interface)

        if count > 0:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

        return res1
    except:
        logger.info ("Unable to execute test case 6")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

def dvr_deployement_test_case_14(controller_ip_list,username):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 7:     Verify that L3 HA must be disabled.                                =====")
    logger.info("==========================================================================================================")
    global res
    global vm
    global float_ip
    for controller_ip in controller_ip_list:
        try:
            ssh_obj.ssh_to(logger, controller_ip, username)
            res = ssh_obj.execute_command_return_output(logger, "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf | grep \"l3_ha=False\"")
            logger.info (res)
            if "l3_ha=False" in str(res.split("\n")):
                logger.info ("TEST SUCCESSFUL")
            else:
                logger.info ("TEST FAILED")
            ssh_obj.ssh_close()
        except:
            logger.info ("Unable to execute test case 7")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

#===============pointer
def dvr_deployement_test_case_15(compute_list, username,network_name,cidr,gateway_ip,subnet_name,
                                       router_name,port_name,server_name,image_name,flavor_name,secgroup_name,zone):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 8:     Create the router and attach an instance to it.                    =====")
    logger.info("====     Verify namespace qrouter is created on the Compute node where instance is scheduled.        =====")
    logger.info("==========================================================================================================")
    try:
        # [network_id, router_id, server_id, str(server_ip), str(f_ip_munch.floating_ip_address)]
        list_return = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name,
                                                                                      network_name, subnet_name,
                                                                                      router_name, port_name, zone,
                                                                                      cidr,
                                                                                      gateway_ip, flavor_name,
                                                                                      image_name,
                                                                                      secgroup_name,
                                                                                      assign_floating_ip=False)

        r_id = conn_create.get_router(
            router_name
        ).id
        namespace_id = "qrouter-%s"%r_id
        ###In case we get a list of compute node ips
        if zone=="nova0":
            compute_ip = compute_list[0]
        elif zone=="nova1":
            compute_ip = compute_list[1]
        elif zone == "nova2":
            compute_ip = compute_list[2]
        else:
            logger.info ("This zone %s dosen't exists"%zone)

        ssh_obj.ssh_to(logger, compute_ip, username)
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns")

        if namespace_id in res:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        ssh_obj.ssh_close()
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)
        return namespace_id
    except:
        logger.info ("Unable to execute test case 8")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

def dvr_deployement_test_case_16(compute_list, username, network_name, cidr, gateway_ip, subnet_name,
                                       router_name, port_name, server_name, image_name, flavor_name, secgroup_name, zone):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 9:     Associate the floating ip to the instance                         =====")
    logger.info("====         verify that namespace for floating Ip 'fip' is created on that Compute node             =====")
    logger.info("==========================================================================================================")
    try:
        net = creation_object.os_network_creation(logger, conn_create, network_name, cidr, subnet_name, gateway_ip)
        rout = creation_object.os_router_creation(logger, conn_create,router_name,port_name,network_name)
        ser = creation_object.os_server_creation(logger, conn_create,server_name,flavor_name,image_name,network_name,secgroup_name,zone)
        flot = creation_object.os_floating_ip_creation_assignment(logger, conn_create, server_name)
        # pdb.set_trace()
        f_id = str(rout.external_gateway_info["network_id"])

        # delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
        #                                             router_name, port_name)


        namespace_id = "fip-%s"%f_id
        if zone=="nova0":
            compute_ip = compute_list[0]
        elif zone=="nova1":
            compute_ip = compute_list[1]
        elif zone == "nova2":
            compute_ip = compute_list[2]
        else:
            logger.info ("This zone %s dosen't exists"%zone)

        ssh_obj.ssh_to(logger, compute_ip, username)
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns")

        if namespace_id in res:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        ssh_obj.ssh_close()
        pdb.set_trace()
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)
        return namespace_id
    except:
        logger.info ("Unable to execute test case 9")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                    router_name, port_name)

def dvr_deployement_test_case_17():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 10:    Verify that metadata agent distributed on all Compute nodes.       =====")
    logger.info("==========================================================================================================")
    #source overcloudrc file
    count = 0
    try:
        #res1 = ssh_obj.locally_execute_command("neutron agent-list --agent-type=\"L3 agent\"")# --agent-type="l3_agent"")
        # pdb.set_trace()
        res1 = ssh_obj.locally_execute_command("openstack network agent list --agent-type metadata")
        out = res1.split("\n")[6].split("|")[3]
        for i in range(6, 9):
            out = res1.split("\n")[i].split("|")[3]
            if "compute-0" in out or "compute-1" in out or "compute-2" in out:
                logger.info ("%s found" % out)
                count += 1
            else:
                logger.info ("Test Failed")
                break
        if count == 3:
            logger.info ("TEST SUCCESSFUL")

        return out
    except:
        logger.info ("Unable to execute test case 10")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_18(compute_ip_list, controller_ip_list, username):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 11:    Verify L2population enabled on all compute and controller nodes.   =====")
    logger.info("==========================================================================================================")
    try:
        for compute_ip in compute_ip_list:
            logger.info ("Checking in Compute: %s"%compute_ip)
            ssh_obj.ssh_to(logger, compute_ip, username)
            res = ssh_obj.execute_command_return_output(logger, "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/ml2_conf.ini | grep \"mechanism_drivers=openvswitch,l2population\"")
            logger.info (res)
            #ovs,l2population
            if "mechanism_drivers=openvswitch,l2population" in str(res.split("\n")):
                logger.info ("COMPUTE TEST SUCCESSFUL")
            else:
                logger.info ("COMPUTE TEST FAIlED")
            ssh_obj.ssh_close()

        for controller_ip in controller_ip_list:
            ssh_obj.ssh_to(logger, controller_ip, username)
            logger.info ("Checking in Controller: %s" % controller_ip)
            res = ssh_obj.execute_command_return_output(logger, "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/ml2_conf.ini | grep \"mechanism_drivers=openvswitch,l2population\"")
            logger.info (res)
            if "mechanism_drivers=openvswitch,l2population" in str(res.split("\n")):
                logger.info ("CONTROLLER TEST SUCCESSFUL")
            else:
                logger.info ("CONTROLLER TEST FAIlED")
            ssh_obj.ssh_close()
        return res

    except:
        logger.info ("Unable to execute test case 11")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_19(compute_ip_list, username, network_name, subnet_name, router_name, port_name,
                                 server_name, image_name, flavor_name, secgroup_name, zone, cidr, gateway_ip):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 12:     Verify traffic from outside the network to instance               =====")
    logger.info("====                     should go through the Floating IP namespace on the compute node.            =====")
    logger.info("==========================================================================================================")
    global float_ip
    try:
        director_ip = stamp_data["director_node_ip"]
        net = creation_object.os_network_creation(logger, conn_create, network_name, cidr, subnet_name, gateway_ip)
        rout = creation_object.os_router_creation(logger, conn_create, router_name, port_name, network_name)
        ser = creation_object.os_server_creation(logger, conn_create, server_name, flavor_name, image_name, network_name,
                                                 secgroup_name, zone)
        flot = creation_object.os_floating_ip_creation_assignment(logger, conn_create, server_name)

        f_id = str(rout.external_gateway_info["network_id"])
        time.sleep(50)
        # pdb.set_trace()
        private_ip = str(conn_create.get_server(name_or_id=server_name).accessIPv4)
        floating_ip = flot.floating_ip_address
        network_id = str(conn_create.get_network(network_name).id)
        router_id = str(conn_create.get_router(router_name).id)
        namespace_id = str("qdhcp-%s" % str(network_id))
        interface_name_tc19 = "fg"
        fip_namespace_id = str("fip-%s" % str(f_id))

        logger.info (network_id)
        logger.info (namespace_id)
        logger.info (router_id)
        logger.info (fip_namespace_id)
        logger.info (floating_ip)
        logger.info (private_ip)
        # pdb.set_trace()
        comp_ip = None
        for compute_ip in compute_ip_list:
            ssh_obj.ssh_to(logger, compute_ip, username)
            res1 = ssh_obj.execute_command_return_output(logger, "sudo ip netns")
            if fip_namespace_id in res1:
                comp_ip = compute_ip
                ssh_obj.ssh_close()
                break
            else:
                logger.info ("fip namespace not found in compute %s" % comp_ip)
                ssh_obj.ssh_close()
        # pdb.set_trace()
        ssh_obj.ssh_to(logger, comp_ip, username)
        ssh_obj.send_key_if_not_present(logger, destination_path="/home/heat-admin/ssh-key.pem")
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns exec %s ip a | grep %s" %
                                                    (fip_namespace_id, interface_name_tc19))
        out = res.split("\n")
        interface_list = []
        for line in out:
            if interface_name_tc19 in str(line):
                try:
                    int_f = line.split(":")[1].strip()
                    logger.info (int_f)
                    interface_list.append(int_f)
                except:
                    pass
        logger.info (interface_list)
        ssh_obj.ssh_close()
        count = 0
        # pdb.set_trace()
        for interface in interface_list:
            ssh_2 = ssh_obj.start_second_session()
            ssh_2.connect(hostname=comp_ip, username=username)
            tcpres = execute_tcp_dump(session=ssh_2, timeout=30, namespace_id=fip_namespace_id, interface=interface)
            check = ssh_obj.locally_ping_check(logger, ip=str(floating_ip))
            res1 = str(stdout_a.read())
            ssh_2.close()
            logger.info(tcpres)
            logger.info(check)
            logger.info (res1)
            if "%s > %s" % (director_ip, floating_ip) in res1 and "%s > %s" % (floating_ip, director_ip) in res1:
                logger.info("TEST SUCCESSFUL for interface %s" % interface)
                count += 1
            else:
                logger.info("TEST FAILED for interface %s" % interface)



        if count > 0:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

        return res1

    except:
        logger.info ("Unable to execute test case 12")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        ssh_obj.ssh_close()
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

def dvr_deployement_test_case_20(compute_ip_list,username, server1_name, server2_name, network1_name,
                                                      network2_name,
                                                      subnet1_name, subnet2_name,
                                                      router_name, port1_name, port2_name, zone, cidr1,
                                                      gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip): ###========zone =  nova2
    logger.info("==========================================================================================================")
    logger.info("====  DVR TEST CASE 13:     Down the L3 agent on one of compute node and send traffic from this node.=====")
    logger.info("==========================================================================================================")
    try:

        # [network_id, router_id, server_id, str(server_ip), str(f_ip_munch.floating_ip_address)]
        # list_return = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name,
        #                                                                               network_name, subnet_name,
        #                                                                               router_name, port_name, zone,
        #                                                                               cidr,
        #                                                                               gateway_ip, flavor_name,
        #                                                                               image_name,
        #                                                                               secgroup_name,
        #                                                                               assign_floating_ip=True)
        #fp1,pp1,fp2,pp2
        ip_list = creation_object.create_2_instances_on_same_compute_dif_network(logger, conn_create, server1_name, server2_name, network1_name, network2_name,
                                                      subnet1_name, subnet2_name,
                                                      router_name, port1_name, port2_name, zone, cidr1,
                                                      gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip)
        logger.info (ip_list)
        if zone1 == "nova0":
            compute_ip = compute_ip_list[0]
        elif zone1 == "nova1":
            compute_ip = compute_ip_list[1]
        else:
            compute_ip = compute_ip_list[2]

        ssh_obj.ssh_to(logger, compute_ip, username)
        # p = ssh_obj.execute_command_return_output(logger, "sudo systemctl stop neutron-l3-agent.service")
        logger.info (p)
        p = ssh_obj.execute_command_return_output(logger, "sudo docker ps | grep l3")
        logger.info (p)
        ssh_obj.ssh_close()

        time.sleep(50)
        ssh_obj.ssh_to(logger, ip_list[0], data["static_image"], key_file_name=data["key_file_path"])
        # res = ssh_obj.execute_command_return_output(logger, "sudo ")
        res = ssh_obj.simple_ping_check(logger, ip_list[3])
        logger.info (res)
        ssh_obj.ssh_close()

        # delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name, network1_name,
        #                                               network2_name,
        #                                               router_name, port1_name, port2_name)

        if res==0:
            logger.info("TEST SUCCESSFUL")
        else:
            logger.info("TEST FAILED")
        pdb.set_trace()
        ssh_obj.ssh_to(logger, compute_ip, username)
        p = ssh_obj.execute_command_return_output(logger, "sudo systemctl start neutron-l3-agent.service")
        logger.info (p)
        p = ssh_obj.execute_command_return_output(logger, "sudo systemctl status neutron-l3-agent.service")
        logger.info (p)
        ssh_obj.ssh_close()

        ##ssh to instance on compute node
        ##ping the instance on another nework
        ##the ping should fail
    except:
        logger.info ("Unable to execute test case 13")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name, network1_name,
                                                      network2_name,
                                                      router_name, port1_name, port2_name)

def dvr_deployement_test_case_21(compute_ip, username):#####################SKIPPED###########
    try:
        ssh_obj.ssh_to(logger, compute_ip, username)
        ssh_obj.execute_command_only(logger, "sudo reboot")
        time.sleep(5)
        global res
        ssh_obj.ssh_to(logger, compute_ip,username)
        res = ssh_obj.execute_command_return_output(logger, "sudo docker ps | grep neutron_l3_agent")
        #pdb.set_trace()
        out = res.split("\n")
        logger.info (out)
        l3_agent_id_control = str(out[0].split(" ")[0])
        logger.info (l3_agent_id_control.strip())
        ssh_obj.execute_command_only(logger, "sudo docker exec -it %s bash" % l3_agent_id_control)
        ssh_obj.execute_command_show_output(logger, "cat /etc/neutron/l3_agent.ini | grep agent_mode")
        if "#agent_mode = dvr_snat" in str(res.split("\n")):
            logger.info ("TEST SUCCESSFUL")
        else:
            logger.info ("TEST FAILED")
        ssh_obj.ssh_close()
        ##repeate for all compute nodes
        return l3_agent_id_control
    except:
        logger.info ("Unable to execute test case 19")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_22(compute_ip_list, username, server_name, network_name, subnet_name, router_name,
                                 port_name, zone, cidr, gateway_ip, flavor_name, image_name, secgroup_name):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 14:   Delete instance the compute node see router namespace still exits.  =====")
    logger.info("==========================================================================================================")
    try:
        # [network_id, router_id, server_id, str(server_ip), str(f_ip_munch.floating_ip_address)]
        list_return = creation_object.create_1_instances_on_same_compute_same_network(logger, conn_create, server_name,
                                                                                      network_name, subnet_name,
                                                                                      router_name, port_name, zone,
                                                                                      cidr,
                                                                                      gateway_ip, flavor_name,
                                                                                      image_name,
                                                                                      secgroup_name,
                                                                                      assign_floating_ip=False)

        qrouter_namespace = "qrouter-%s"%list_return[1]
        if zone == "nova0":
            compute_ip = compute_ip_list[0]
        elif zone == "nova1":
            compute_ip = compute_ip_list[1]
        else:
            compute_ip = compute_ip_list[2]

        ssh_obj.ssh_to(logger, compute_ip, username)
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns")
        if qrouter_namespace in res:
            logger.info("Qrouter namespace is present in Compute Node Before Deletion")
        else:
            logger.info("Qrouter namespace dosent exists")
        ssh_obj.ssh_close()

        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)
        ssh_obj.ssh_to(logger, compute_ip, username)
        res = ssh_obj.execute_command_return_output(logger, "sudo ip netns")


        if qrouter_namespace not in res:
            logger.info ("TEST SUCCESSFUL")
        else:
            logger.info ("TEST FAILED")
        ssh_obj.ssh_close()
    except:
        logger.info ("Unable to execute test case 14")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        delete_object.delete_1_instance_and_router_with_1_network(logger, conn_delete, server_name, network_name,
                                                                  router_name, port_name)

# def dvr_deployement_test_case_23(controller_ip, username):#####################SKIPPED###########
#     try:
#         ssh_obj.ssh_to(logger, controller_ip, username)
#         ssh_obj.execute_command_only(logger, "sudo reboot")
#         time.sleep(5)
#         global res
#         ssh_obj.ssh_to(logger, controller_ip,username)
#         res = ssh_obj.execute_command_return_output(logger, "sudo docker ps | grep neutron_l3_agent")
#         #pdb.set_trace()
#         out = res.split("\n")
#         logger.info (out)
#         l3_agent_id_control = str(out[0].split(" ")[0])
#         logger.info (l3_agent_id_control.strip())
#         ssh_obj.execute_command_only(logger, "sudo docker exec -it %s bash" % l3_agent_id_control)
#         ssh_obj.execute_command_show_output(logger, "cat /etc/neutron/l3_agent.ini | grep agent_mode")
#         if "#agent_mode = dvr_snat" in str(res.split("\n")):
#             logger.info ("TEST SUCCESSFUL")
#         else:
#             logger.info ("TEST FAILED")
#         ssh_obj.ssh_close()
#         ##repeate for all controller nodes
#         return l3_agent_id_control
#     except:
#         logger.info ("Unable to execute test case 19")
#         logger.info ("\nError: " + str(sys.exc_info()[0]))
#         logger.info ("Cause: " + str(sys.exc_info()[1]))
#         logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
# ===================================================================================================================================================================================================

#===================IPERF3
def dvr_deployement_test_case_29():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 15:     Perform network bandwidth test                                    =====")
    logger.info("====                 with 2 instance on same tenant network and on same compute node                 =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth= iperf3_funcs.create_2_instances_on_same_compute_same_network_and_exec_iperf3(logger)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 15")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_30():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 16:     Perform network bandwidth test                                    =====")
    logger.info("====                 with 2 instance on diff tenant network and on same compute node                 =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth = iperf3_funcs.create_2_instances_on_same_compute_diff_network_and_exec_iperf3(logger)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 16")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_31():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 17:     Perform network bandwidth test                                    =====")
    logger.info("====                 with 2 instance on same tenant network and on diff compute node                 =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth = iperf3_funcs.create_2_instances_on_diff_compute_same_network_and_exec_iperf3(logger)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 17")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_32():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 18:     Perform network bandwidth test                                    =====")
    logger.info("====                 with 2 instance on diff tenant network and on diff compute node                 =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth = iperf3_funcs.create_2_instances_on_diff_compute_diff_network_and_exec_iperf3(logger)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 18")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_35():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 19:     Perform network bandwidth test                                    =====")
    logger.info("====        with 2 instance on diff tenant network and on same compute node with FloatingIP          =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth = iperf3_funcs.create_2_instances_on_same_compute_diff_network_and_exec_iperf3(logger, check_bw_by_floating_ip=True)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 19")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_36():
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 20:     Perform network bandwidth test                                    =====")
    logger.info("====      with 2 instance on diff tenant network and on diff compute node with FloatingIP            =====")
    logger.info("==========================================================================================================")
    try:
        Bandwidth = iperf3_funcs.create_2_instances_on_diff_compute_diff_network_and_exec_iperf3(logger, check_bw_by_floating_ip=True)

        if Bandwidth is not None:
            logger.info ("TEST SUCCESSFUL")
            return Bandwidth
        else:
            logger.info ("TEST FAILED")
    except:
        logger.info ("Unable to execute test case 20")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_37(logger, conn_create, flavor_name, disk_size, ram_size, vcpu_number,
                                 server_name, image_name, network_name, secgroup_name, availability_zone, keypair_name):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 21:            DVR should work fine with NUMA.                            =====")
    logger.info("==========================================================================================================")
    """1. Go to compute node.
        2. scource <overcloudrc>
        3. Run the command openstack flavor create <flavor-name> --disk 40 --ram 4096 --vcpu 2
         4. Run NUMA script with the flavor name
         5. Run the command openstack server create --image <OS> --key-name <Keypair name> --availability-zone <compute node > --nic net-id=<Tenant net id> --flavor <flavor name> <instance name>
    """
    try:
        numa_flavor = creation_object.os_flavor_creation(logger, conn_create, name=flavor_name, ram=ram_size,
                                                         vcpus=vcpu_number, disk=disk_size)
        # Run NUMA script with the flavor name

        numa_server = creation_object.os_server_creation(logger, conn_create, server_name, flavor_name, image_name, network_name, secgroup_name,
                               availability_zone, key_name=keypair_name)

        flag=creation_object.check_component_in_list(logger, conn_create, component_list_name="server", component_name=server_name)

        if flag==1:
            logger.info("TEST SUCCESSFUL")
            delete_object.os_delete_server(logger, conn_delete, server_name)
        else:
            logger.info("TEST FAILED")
            delete_object.os_delete_server(logger, conn_delete, server_name)
    except:
        logger.info ("Unable to execute test case 21")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_38(flavor_name, disk_size, ram_size, vcpu_number,
                                 server_name, image_name, network_name, secgroup_name, availability_zone, keypair_name):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 22:            DVR should work fine with HUGEPAGES.                       =====")
    logger.info("==========================================================================================================")
    """1. Go to compute node.
        2. scource <overcloudrc>
        3. Run the command openstack flavor create <flavor-name> --disk 40 --ram 4096 --vcpu 2
         4. Run HugePages script with the flavor name
         5. Run the command openstack server create --image <OS> --key-name <Keypair name> --availability-zone <compute node > --nic net-id=<Tenant net id> --flavor <flavor name> <instance name>
    """
    try:
        hugepages_flavor = creation_object.os_flavor_creation(logger, conn_create, name=flavor_name, ram=ram_size,
                                                         vcpus=vcpu_number, disk=disk_size)
        # Run HUGEPAGES script with the flavor name

        hugepages_server = creation_object.os_server_creation(logger, conn_create, server_name, flavor_name, image_name, network_name, secgroup_name,
                               availability_zone, key_name=keypair_name)

        flag=creation_object.check_component_in_list(logger, conn_create, component_list_name="server", component_name=server_name)

        if flag==1:
            logger.info("TEST SUCCESSFUL")
            delete_object.os_delete_server(logger, conn_delete, server_name)
        else:
            logger.info("TEST FAILED")
            delete_object.os_delete_server(logger, conn_delete, server_name)
    except:
        logger.info ("Unable to execute test case 22")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

#=====================IPERF3
def dvr_deployement_test_case_39(size, name, image):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 23:                       Create Volume.                                  =====")
    logger.info("==========================================================================================================")
    # global result
    try:
        result = creation_object.os_create_volume(logger, conn_create,size,name,image)
        # pdb.set_trace()
        vol = conn_create.get_volume(name).name

        if name in vol:
            logger.info("TEST SUCCESSFUL")
            conn_delete.delete_volume(name_or_id=name)
        else:
            logger.info("TEST FAILED")
            conn_delete.delete_volume(name_or_id=name)
    except:
        logger.info ("Unable to execute test case 23")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_40(server, volume , attach=None, detach=None):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 24:     Attach/Detach Volume to VM instance.                              =====")
    logger.info("==========================================================================================================")
    global result
    try:
        if attach:
            result = creation_object.os_attach_volume(logger, conn_create,server,volume)
        elif detach:
            result = creation_object.os_detach_volume(logger, conn_create, server, volume)
        else:
            logger.info("Specify attach / detach = True")
        return result
    except:
        logger.info ("Unable to execute test case 24")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

def dvr_deployement_test_case_41(server_name,flavor_name,network_name,secgroup_name,availability_zone,boot_volume):
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 25:     Boot from Volume.                                                 =====")
    logger.info("==========================================================================================================")
    global result
    try:
        result = creation_object.os_server_creation_boot(logger, conn_create,server_name,flavor_name,network_name,secgroup_name,availability_zone,boot_volume)
        get_ser = get_server(name_or_id=server_name, filters=None)
        get_vol = get_volume(name_or_id, filters=None)
        logger.info (get_ser)
        logger.info (get_vol)
        return result
    except:
        logger.info ("Unable to execute test case 25")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def dvr_deployement_test_case_42(server_name,flavor_name,network_name,secgroup_name,availability_zone,boot_volume):######SKIP###########
    logger.info("==========================================================================================================")
    logger.info("====         DVR TEST CASE 26:     Boot from Volume Snapshot.                                        =====")
    logger.info("==========================================================================================================")
    global result
    try:
        result = creation_object.os_server_creation_boot(logger, conn_create,server_name,flavor_name,network_name,secgroup_name,availability_zone,boot_volume)
        get_ser = get_server(name_or_id=server_name, filters=None)
        get_vol = get_volume(name_or_id, filters=None)
        logger.info (get_ser)
        logger.info (get_vol)
        return result
    except:
        logger.info ("Unable to execute test case 26")
        logger.info ("\nError: " + str(sys.exc_info()[0]))
        logger.info ("Cause: " + str(sys.exc_info()[1]))
        logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


def test_case_30():
    # creating 2 instances of different compute and different tenant network

    server1_name = "test_vm1"
    server2_name = "test_vm2"
    network_name = "test_network"
    network1_name = "test_network1"
    network2_name = "test_network2"
    subnet_name = "test_sub"
    subnet1_name = "test_sub1"
    subnet2_name = "test_sub2"
    router_name = "test_router"
    port_name = "test_port"
    port1_name = "test_port1"
    port2_name = "test_port2"
    zone = "sriov-zone"
    zone1 = "sriov-zone"
    zone2 = "sriov-zone"
    cidr = "192.168.70.0/24"
    gateway_ip = "192.168.70.1"
    cidr1 = "192.168.30.0/24"
    gateway_ip1 = "192.168.30.1"
    cidr2 = "192.168.40.0/24"
    gateway_ip2 = "192.168.40.1"
    flavor_name = "last"
    image_name = "last"
    secgroup_name = "last"
    assign_floating_ip = True



    #####################################################################################################################
    ############################Senario 1 Create_2_Instances_on_Different_Compute_Diffferent_Network#####################
    #####################################################################################################################
    # list_of_ips = creation_object.create_2_instances_on_dif_compute_dif_network(conn, server1_name, server2_name,
    #                                                                             network1_name, network2_name,
    #                                                                             subnet1_name, subnet2_name,
    #                                                                             router_name, port1_name, port2_name,
    #                                                                             zone1, zone2, cidr1,
    #                                                                             gateway_ip1, cidr2, gateway_ip2,
    #                                                                             flavor_name, image_name,
    #                                                                             secgroup_name, assign_floating_ip)
    #####################################################################################################################
    ######################################Senario 2 Create_2_Instances_on_Same_Compute_Same_Network######################
    #####################################################################################################################
    # pdb.set_trace()
    # list_of_ips = creation_object.create_2_instances_on_same_compute_same_network(conn, server1_name, server2_name,
    #                                                                             network_name,
    #                                                                             subnet_name,
    #                                                                             router_name,
    #                                                                             port_name,
    #                                                                             zone,
    #                                                                             cidr,
    #                                                                             gateway_ip,
    #                                                                             flavor_name, image_name,secgroup_name,
    #                                                                             assign_floating_ip)
    #

    #####################################################################################################################
    ##################################Senario 3 Create_2_Instances_on_Different_Compute_Same_Network#####################
    #####################################################################################################################
    # list_of_ips = creation_object.create_2_instances_on_dif_compute_same_network(logger, conn_create, server1_name, server2_name,
    #                                                                             network_name,
    #                                                                             subnet_name,
    #                                                                             router_name,
    #                                                                             port_name,
    #                                                                             zone1,zone2,
    #                                                                             cidr,
    #                                                                             gateway_ip,
    #                                                                             flavor_name, image_name,secgroup_name,
    #                                                                             assign_floating_ip)
    #####################################################################################################################
    ##################################Senario 4 Create_2_Instances_on_Same_Compute_Diffferent_Network####################
    #####################################################################################################################
    # list_of_ips = creation_object.create_2_instances_on_same_compute_dif_network(conn, server1_name, server2_name,
    #                                                                             network1_name, network2_name,
    #                                                                             subnet1_name, subnet2_name,
    #                                                                             router_name, port1_name, port2_name,
    #                                                                             zone, cidr1,
    #                                                                             gateway_ip1, cidr2, gateway_ip2,
    #                                                                             flavor_name, image_name,
    #                                                                             secgroup_name, assign_floating_ip)


    # logger.info list_of_ips




    #####################################################################################################################
    ####################       DELETE_2_Instances_on_Different_Compute_Diffferent_Network          ######################
    ####################       DELETE_2_Instances_on_Same_Compute_Diffferent_Network                #####################
    #####################################################################################################################
    # delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name, network1_name, network2_name,
    #                                               router_name, port1_name, port2_name)





    #####################################################################################################################
    ####################       DELETE_2_Instances_on_Different_Compute_Same_Network                 #####################
    ####################       DELETE_2_Instances_on_Same_Compute_Same_Network                      #####################
    #####################################################################################################################
    # delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name, network_name, router_name, port_name)



    #####################################################################################################################
    ##################################              IPERF CREATION COMMAND                          #####################
    #####################################################################################################################
    #
    # username = "centos"
    # key_file_path = "/home/stack/key.pem"
    # client_ssh_ip = "192.168.10.204" # public ip of client
    # client_iperf_ip = "192.168.40.17" # private ip client
    # server_ssh_ip ="192.168.10.208" # public ip of server
    # server_iperf_ip = "192.168.40.16" # private ip of server
    # pdb.set_trace()
    #
    # Bandwidth=ssh_obj.check_bandwidth_private_ip(logger, username, client_ssh_ip, server_ssh_ip, client_iperf_ip,
    #                                server_iperf_ip, password=None, with_key_pair_flag=False, key_file_path=None)


# res1 = dvr_deployement_test_case_14("192.168.24.11","heat-admin")
# logger.info res1



#delete_vm_network_router()

# test_case_30()
controller_ip = "192.168.24.11"
compute_ip = "192.168.24.10"
username = "heat-admin"
server_name="test_vm"
server1_name = "test_vm1"
server2_name = "test_vm2"
network_name = "test_network"
network1_name = "test_network1"
network2_name = "test_network2"
subnet_name = "test_sub"
subnet1_name = "test_sub1"
subnet2_name = "test_sub2"
router_name = "test_router"
port_name = "test_port"
port1_name = "test_port1"
port2_name = "test_port2"
zone = "nova0"
zone1 = "nova1"
zone2 = "nova2"
cidr = "192.168.70.0/24"
gateway_ip = "192.168.70.1"
cidr1 = "192.168.30.0/24"
gateway_ip1 = "192.168.30.1"
cidr2 = "192.168.40.0/24"
gateway_ip2 = "192.168.40.1"
flavor_name = "m1.medium"
image_name = "centos"
secgroup_name = "e616eefa-86c8-4993-b8bf-3fc9d1d04003"
assign_floating_ip = False
#test_case_30()
# dvr_deployement_test_case_11(controller_ip,username,router_name,
#                                                         network1_name,network2_name,
#                                                         subnet1_name,subnet2_name,
#                                                         port1_name,port2_name,
#                                                         server1_name,server2_name,
#                                                         image_name,flavor_name,secgroup_name,
#                                                         zone1,zone2, cidr1,gateway_ip1,
#                                                         cidr2, gateway_ip2)

# dvr_deployement_test_case_16(username,network_name,cidr,gateway_ip,subnet_name,router_name,port_name,server_name,image_name,flavor_name,secgroup_name,zone)
# dvr_deployement_test_case_29(username, server1_name, server2_name, network_name, subnet_name,
#                                                     router_name, port_name, zone, cidr,
#                                                     gateway_ip, flavor_name, image_name,
#                                                     secgroup_name, assign_floating_ip)
# dvr_deployement_test_case_29(username)

#
# list_of_ips = creation_object.create_2_instances_on_dif_compute_dif_network(logger, conn_create, server1_name, server2_name, network1_name, network2_name,
# 													  subnet1_name, subnet2_name,
# 													  router_name, port1_name, port2_name, zone1, zone2, cidr1,
# 													  gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
# 													  secgroup_name, assign_floating_ip)
#
# logger.info list_of_ips
# list_of_ips = dvr_deployement_test_case_30(username, server1_name, server2_name, network1_name, network2_name, subnet1_name, subnet2_name,
#                                  router_name, port1_name, port2_name, zone, cidr1,gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
#                                  secgroup_name, assign_floating_ip)
# logger.info list_of_ips

# res = dvr_deployement_test_case_11(controller_ip,username,router_name,
#                                                         network1_name,network2_name,
#                                                         subnet1_name,subnet2_name,
#                                                         port1_name,port2_name,
#                                                         server1_name,server2_name,
#                                                         image_name,flavor_name,secgroup_name,
#                                                         zone1,zone2, cidr1,gateway_ip1,
#                                                         cidr2, gateway_ip2)
# logger.info res

# dvr_deployement_test_case_12_13(controller_ip,username,network_name,server_name,image_name,flavor_name,secgroup_name,zone,assign_floating_ip)



#===============pointer
controller = [stamp_data["cntl0"],stamp_data["cntl1"],stamp_data["cntl2"]]
compute = [stamp_data["cmpt0"], stamp_data["cmpt1"], stamp_data["cmpt2"]]
stamp_user="heat-admin"
logger.info ("Controller ip's %s" %controller)
logger.info ("Compute ip's %s" %compute)
#
# dvr_deployement_test_case_39(size=20, name=data["static_volume"],image=data["static_image"])

# dvr_deployement_test_case_29()
#
# dvr_deployement_test_case_31()
#
# dvr_deployement_test_case_32()
#
# dvr_deployement_test_case_30()



# dvr_deployement_test_case_22(compute_ip_list=compute, username=stamp_user, server_name=data["server_name"],
#                              network_name=data["network_name"],subnet_name=data["subnet_name"], router_name=data["router_name"],
#                              port_name=data["port_name"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"],
#                              flavor_name=data["static_flavor"], image_name=data["static_image"], secgroup_name=data["static_secgroup"])

dvr_deployement_test_case_20(compute_ip_list=compute,username=stamp_user, server1_name=data["server1_name"], server2_name=data["server2_name"],
                             network1_name=data["network1_name"],
                                                      network2_name=data["network2_name"],
                                                      subnet1_name=data["subnet1_name"], subnet2_name=data["subnet2_name"],
                                                      router_name=data["router_name"], port1_name=data["port1_name"], port2_name=data["port2_name"],
                             zone=data["zone3"], cidr1=data["cidr1"],
                                                      gateway_ip1=data["gateway_ip1"], cidr2=data["cidr2"], gateway_ip2=data["gateway_ip2"],
                             flavor_name=data["static_flavor"], image_name=data["static_image"],
                                                      secgroup_name=data["static_secgroup"], assign_floating_ip=True)#######FAILED

# dvr_deployement_test_case_19(compute_ip_list=compute, username=stamp_user, network_name=data["network_name"],
#                           subnet_name=data["subnet_name"], router_name=data["router_name"], port_name=data["port_name"], server_name=data["server_name"],
#                                  image_name=data["static_image"], flavor_name=data["static_flavor"],
#                              secgroup_name=data["static_secgroup"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"])


# dvr_deployement_test_case_18(compute, controller, stamp_user)
# # # #
# dvr_deployement_test_case_17()
#
# dvr_deployement_test_case_16(compute_list=compute, username=stamp_user,network_name=data["network_name"],cidr=data["cidr"],
#                                  gateway_ip=data["gateway_ip"],subnet_name=data["subnet_name"],
#                                        router_name=data["router_name"],port_name=data["port_name"],
#                                  server_name=data["server_name"],image_name=data["rhel_image"],
#                                  flavor_name=data["static_flavor"],secgroup_name=data["static_secgroup"],zone=data["zone1"])
#
#
# dvr_deployement_test_case_15(compute_list=compute, username=stamp_user,network_name=data["network_name"],cidr=data["cidr"],
#                                  gateway_ip=data["gateway_ip"],subnet_name=data["subnet_name"],
#                                        router_name=data["router_name"],port_name=data["port_name"],
#                                  server_name=data["server_name"],image_name=data["rhel_image"],
#                                  flavor_name=data["static_flavor"],secgroup_name=data["static_secgroup"],zone=data["zone1"])


# dvr_deployement_test_case_14(controller, stamp_user)#DONE

# dvr_deployement_test_case_13(controller_ip_list=controller, username=stamp_user, network_name=data["network_name"],
#                           subnet_name=data["subnet_name"], router_name=data["router_name"], port_name=data["port_name"], server_name=data["server_name"],
#                                  image_name=data["static_image"], flavor_name=data["static_flavor"],
#                              secgroup_name=data["static_secgroup"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"])

# dvr_deployement_test_case_12(controller_ip_list=controller, username=stamp_user, network_name=data["network_name"],
#                              subnet_name=data["subnet_name"], router_name=data["router_name"], port_name=data["port_name"], server_name=data["server_name"],
#                                  image_name=data["static_image"], flavor_name=data["static_flavor"],
#                              secgroup_name=data["static_secgroup"], zone=data["zone1"], cidr=data["cidr"], gateway_ip=data["gateway_ip"])

# dvr_deployement_test_case_11(controller_ip=controller[0], username=stamp_user, router_name=data["router_name"],
#                                                        network1_name=data["network1_name"], network2_name=data["network2_name"],
#                                                        subnet1_name=data["subnet1_name"], subnet2_name=data["subnet2_name"],
#                                                        port1_name=data["port1_name"], port2_name=data["port2_name"],
#                                                        server1_name=data["server1_name"], server2_name=data["server2_name"],
#                                                        image_name=data["static_image"],
#                                                        flavor_name=data["static_flavor"],
#                                                        secgroup_name=data["static_secgroup"],
#                                                        zone1=data["zone2"], zone2=data["zone3"],
#                                                        cidr1=data["cidr1"],gateway_ip1=data["gateway_ip1"],
#                                                        cidr2=data["cidr2"], gateway_ip2=data["gateway_ip2"])

# dvr_deployement_test_case_10()#DONE
# #
# #
# dvr_deployement_test_case_5(compute, stamp_user)#DONE
# #
# #
# dvr_deployement_test_case_4(controller, stamp_user)#DONE

# ssh_obj.ssh_to(logger, "192.168.120.21", "heat-admin")
# ssh_obj.send_key_if_not_present(logger, destination_path="/home/heat-admin/ssh-key.pem")
# check = ssh_obj.ping_check_from_namespace(logger, namespace_id="qdhcp-75499bf9-6c48-4020-b39b-70041377240f", ip_of_instance1="192.168.70.6",
#                                                       username_of_instance="centos",
#                                                       key_file_path_of_node="/home/heat-admin/ssh-key.pem",
#                                                       ip_of_instance2="8.8.8.8")
# ssh_obj.ssh_close()
