from ssh_funcs_api import ssh_functions
from vm_creation import Os_Creation_Modules, data
from delete_os import Os_Deletion_Modules
import time
import sys
import pdb
from source_R8rc import Source_Module

ssh_obj = ssh_functions()
creation_object = Os_Creation_Modules()
delete_object = Os_Deletion_Modules()
conn_create = creation_object.os_connection_creation()
conn_delete = delete_object.os_connection_creation()


# data = creation_object.get_data_from_setup_file()
server_name = data["server_name"]
server1_name = data["server1_name"]
server2_name = data["server2_name"]
network_name = data["network_name"]
network1_name = data["network1_name"]
network2_name = data["network2_name"]
subnet_name = data["subnet_name"]
subnet1_name = data["subnet1_name"]
subnet2_name = data["subnet2_name"]
router_name = data["router_name"]
port_name = data["port_name"]
port1_name = data["port1_name"]
port2_name = data["port2_name"]
zone1 = data["zone1"]
zone2 = data["zone2"]
zone3 = data["zone3"]
cidr = data["cidr"]
gateway_ip = data["gateway_ip"]
cidr1 = data["cidr1"]
gateway_ip1 = data["gateway_ip1"]
cidr2 = data["cidr2"]
gateway_ip2 = data["gateway_ip2"]
static_flavor = data["static_flavor"]
static_image = data["static_image"]
static_secgroup = data["static_secgroup"]
key_file_path = data["key_file_path"]
iperf_package_path = data["iperf_package_path"]


# Checking bandwidth (through iperf3) on private IPs and ssh using public ip
def check_bandwidth_through_private_ip(logger, ips_list, udp_flag, username, packet_size, iperf_client_time):
    instance1_public_ip = ips_list[0]
    instance1_private_ip = ips_list[1]
    instance2_public_ip = ips_list[2]
    instance2_private_ip = ips_list[3]
    bandwidth = None
    # if username == "cirros":
    #     print "Waiting for 10 seconds..."
    #     time.sleep(10)
    # elif username == "centos":
    #     print "Waiting for 50 seconds..."
    #     time.sleep(50)
    # else:
    #     time.sleep(20)
    time.sleep(50)
    for i in range(0,3):
        bandwidth = ssh_obj.check_bandwidth_private_ip(logger, username, udp_flag=udp_flag, client_ssh_ip=instance1_public_ip,
                                                           server_ssh_ip=instance2_public_ip,
                                                           client_iperf_ip=instance1_private_ip,
                                                   server_iperf_ip=instance2_private_ip, iperf_client_time=iperf_client_time,
                                                    packet_size = packet_size, key_file_path=key_file_path)
        if bandwidth == -1:
            logger.info("Unable to execute iperf3. Retying...%s" % i)
            time.sleep(2)
            bandwidth = None
            continue
        else:
            break
    return bandwidth


# Verify Performance with Iperf3 between 2 Instances on Same Compute and Same Tenant Network
def create_2_instances_on_same_compute_same_network_and_exec_iperf3(logger, udp_flag=False, packet_size_list=None,
                                        iperf_client_time=None, assign_floating_ip=True, delete_after_create_flag=True,
                                        check_bw_by_floating_ip=False ,
                                        server1_name=server1_name, server2_name=server2_name, network_name=network_name,
                                        subnet_name=subnet_name, router_name=router_name, port_name=port_name, zone=zone1,
                                        cidr=cidr,gateway_ip=gateway_ip, flavor_name=static_flavor,
                                        image_name=static_image, secgroup_name=static_secgroup):
    result = None
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_same_network(logger, conn_create, server1_name, server2_name,
                                                                network_name, subnet_name,
                                                                router_name, port_name, zone, cidr,
                                                                gateway_ip, flavor_name, image_name,
                                                                secgroup_name, assign_floating_ip)
        logger.info("Two instances Created Successfully.")
        if check_bw_by_floating_ip == True:
            logger.info(">>Will be checking bandwidth through floating IPs.")
            ip_list[1] = ips_list[0]
            ip_list[3] = ips_list[2]
        else:
            logger.info(">>Will be checking bandwidth through private IPs.")
            pass
        if type(packet_size_list) == list:
            logger.info("Packet sizes: %s" % packet_size_list)
            bandwidth = {}
            i = 1
            for packet_size in packet_size_list:
                logger.info("\nIteration %s : For Packet size: %s" % (i, packet_size))
                bw = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                        iperf_client_time=iperf_client_time, packet_size=packet_size)
                bandwidth[packet_size] = bw
                i += 1
        else:
            bandwidth = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                           iperf_client_time=iperf_client_time, packet_size=packet_size_list)
        result = bandwidth
        if delete_after_create_flag:     # Deleting network, router, port and both the instances
            logger.info("Deleting both instances..")
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name, router_name, port_name)
        else:
            logger.info("Note: Both the instances are not deleted!!")
    except:
        logger.info("Error encountered while verifying Performance with Iperf3 between 2 Instances \n on " \
              "Same Compute and Same Tenant Network!")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        logger.info("Deleting both instances..")
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                   network_name, router_name, port_name)
    return result


# Verify Performance with Iperf3 between 2 Instances on Different Compute and Same Tenant Network
def create_2_instances_on_diff_compute_same_network_and_exec_iperf3(logger, udp_flag=False, packet_size_list=None,
                                        iperf_client_time = None, assign_floating_ip=True, delete_after_create_flag=True,
                                        check_bw_by_floating_ip=False ,
                                        server1_name=server1_name, server2_name=server2_name, network_name=network_name,
                                        subnet_name=subnet_name, router_name=router_name, port_name=port_name,
                                        zone1=zone1, zone2=zone2, cidr=cidr, gateway_ip=gateway_ip,
                                        flavor_name=static_flavor, image_name=static_image, secgroup_name=static_secgroup):
    result = None
    try:
        ips_list = creation_object.create_2_instances_on_dif_compute_same_network(logger, conn_create, server1_name, server2_name,
                                                          network_name, subnet_name, router_name, port_name, zone1 ,zone2,
                                                          cidr, gateway_ip, flavor_name, image_name,
                                                          secgroup_name, assign_floating_ip)
        logger.info("Two instances Created Successfully.")
        if check_bw_by_floating_ip == True:
            logger.info(">>Will be checking bandwidth through floating IPs.")
            ip_list[1] = ips_list[0]
            ip_list[3] = ips_list[2]
        else:
            logger.info(">>Will be checking bandwidth through private IPs.")
            pass
        if type(packet_size_list) == list:
            logger.info("Packet sizes: %s" % packet_size_list)
            bandwidth = {}
            i = 1
            for packet_size in packet_size_list:
                logger.info("\nIteration %s : For Packet size: %s" % (i, packet_size))
                bw = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                        iperf_client_time=iperf_client_time, packet_size=packet_size)
                bandwidth[packet_size] = bw
                i += 1
        else:
            bandwidth = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                           iperf_client_time=iperf_client_time, packet_size=packet_size_list)
        result = bandwidth
        if delete_after_create_flag:
            logger.info("Deleting both instances..")
            delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                                       network_name, router_name, port_name)
        else:
            logger.info("Note: Both the instances are not deleted!!")
    except:
        logger.info("Error encountered while verifying Performance with Iperf3 between 2 Instances \n " \
              "on Different Compute and Same Tenant Network!")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        logger.info("Deleting both instances..")
        delete_object.delete_2_instances_and_router_with_1_network(logger, conn_delete, server1_name, server2_name,
                                                               network_name, router_name, port_name)
    return result


# Verify Performance with Iperf3 between 2 Instances on Different Compute and Different Tenant Network
def create_2_instances_on_diff_compute_diff_network_and_exec_iperf3(logger, udp_flag=False, packet_size_list = None,
                                        iperf_client_time = None, assign_floating_ip=True, delete_after_create_flag=True,
                                        check_bw_by_floating_ip=False ,server1_name=server1_name, server2_name=server2_name,
                                        network1_name=network1_name, network2_name=network2_name, subnet1_name=subnet1_name,
                                        subnet2_name=subnet2_name, router_name=router_name, port1_name=port1_name,
                                        port2_name=port2_name, zone1=zone1, zone2=zone2, cidr1=cidr1, gateway_ip1=gateway_ip1,
                                        cidr2=cidr2, gateway_ip2=gateway_ip2,
                                        flavor_name=static_flavor, image_name=static_image, secgroup_name=static_secgroup):
    result = None
    try:
        ips_list = creation_object.create_2_instances_on_dif_compute_dif_network(logger, conn_create, server1_name, server2_name,
                                         network1_name, network2_name, subnet1_name, subnet2_name, router_name,
                                         port1_name, port2_name, zone1, zone2, cidr1, gateway_ip1, cidr2, gateway_ip2,
                                                    flavor_name, image_name, secgroup_name, assign_floating_ip)
        logger.info("Two instances Created Successfully.")
        if check_bw_by_floating_ip == True:
            logger.info(">>Will be checking bandwidth through floating IPs.")
            ip_list[1] = ips_list[0]
            ip_list[3] = ips_list[2]
        else:
            logger.info(">>Will be checking bandwidth through private IPs.")
            pass
        if type(packet_size_list) == list:
            logger.info("Packet sizes: %s" % packet_size_list)
            bandwidth = {}
            i = 1
            for packet_size in packet_size_list:
                logger.info("\nIteration %s : For Packet size: %s" % (i, packet_size))
                bw = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name, iperf_client_time=iperf_client_time,
                                                        packet_size=packet_size)
                bandwidth[packet_size] = bw
                i += 1
        else:
            bandwidth = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                           iperf_client_time=iperf_client_time, packet_size=packet_size_list)
        result = bandwidth
        if delete_after_create_flag:
            logger.info("Deleting both instances..")
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_create, server1_name, server2_name,
                                                    network1_name, network2_name, router_name, port1_name, port2_name)
        else:
            logger.info("Note: Both the instances are not deleted!!")
    except:
        logger.info("Error encountered while verifying Performance with Iperf3 between 2 Instances " \
              "\n on Different Compute and Different Tenant Network!")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        logger.info("Deleting both instances..")
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                                    network1_name, network2_name, router_name,
                                                                    port1_name, port2_name)
    return result


# Verify Performance with Iperf3 between 2 Instances on Same Compute and on Different Tenant Network
def create_2_instances_on_same_compute_diff_network_and_exec_iperf3(logger, udp_flag=False, packet_size_list = None,
                                        iperf_client_time = None, assign_floating_ip=True, delete_after_create_flag=True,
                                        check_bw_by_floating_ip=False, server1_name=server1_name, server2_name=server2_name,
                                        network1_name=network1_name, network2_name=network2_name, subnet1_name=subnet1_name,
                                        subnet2_name=subnet2_name, router_name=router_name, port1_name=port1_name,
                                        port2_name=port2_name, zone=zone1, cidr1=cidr1, gateway_ip1=gateway_ip1,
                                        cidr2=cidr2, gateway_ip2=gateway_ip2, flavor_name=static_flavor, image_name=static_image,
                                        secgroup_name=static_secgroup):
    result = None
    try:
        ips_list = creation_object.create_2_instances_on_same_compute_dif_network(logger, conn_create, server1_name,
                                                        server2_name, network1_name,
                                                       network2_name, subnet1_name, subnet2_name,
                                                      router_name, port1_name, port2_name, zone, cidr1,
                                                      gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip)
        logger.info("Two instances Created Successfully.")
        if check_bw_by_floating_ip == True:
            logger.info(">>Will be checking bandwidth through floating IPs.")
            ip_list[1] = ips_list[0]
            ip_list[3] = ips_list[2]
        else:
            logger.info(">>Will be checking bandwidth through private IPs.")
            pass
        if type(packet_size_list) == list:
            logger.info("Packet sizes: %s" % packet_size_list)
            bandwidth = {}
            i = 1
            for packet_size in packet_size_list:
                logger.info("\nIteration %s : For Packet size: %s" % (i, packet_size))
                bw = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                        iperf_client_time=iperf_client_time, packet_size=packet_size)
                bandwidth[packet_size] = bw
                i += 1
        else:
            bandwidth = check_bandwidth_through_private_ip(logger, ips_list, udp_flag=udp_flag, username=image_name,
                                                           iperf_client_time=iperf_client_time, packet_size=packet_size_list)
        result = bandwidth
        if delete_after_create_flag:
            logger.info("Deleting both instances..")
            delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                    network1_name, network2_name, router_name, port1_name, port2_name)
        else:
            logger.info("Note: Both the instances are not deleted!!")
    except:
        logger.info("Error encountered while verifying Performance with Iperf3 between 2 Instances \n on " \
              "Same Compute and Different Tenant Network!")
        logger.info("\nError: " + str(sys.exc_info()[0]))
        logger.info("Cause: " + str(sys.exc_info()[1]))
        logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
        logger.info("Deleting both instances..")
        delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete, server1_name, server2_name,
                                                    network1_name, network2_name, router_name, port1_name, port2_name)
    return result


# pdb.set_trace()
# create_2_instances_on_same_compute_diff_network_and_exec_iperf3()


