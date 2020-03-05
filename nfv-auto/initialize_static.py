from vm_creation import Os_Creation_Modules, data, stamp_data
from delete_os import Os_Deletion_Modules
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import time
import pdb
import sys
import json
from source_R8rc import Source_Module

feature_name = "Initializing_Static"

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


obj=Os_Creation_Modules()
conn=obj.os_connection_creation()
# logger.info("Adding Aggregate and zone for each Compute Node")
#=================R146===================#

# list = ["r146-dell-compute-0.r146.nfv.lab",
#     "r146-dell-compute-1.r146.nfv.lab", "r146-dell-compute-2.r146.nfv.lab"]
# c = 0
# for i in list:
#     obj.os_aggregate_creation_and_add_host(logger, conn, "nova%s"%c, availablity_zone="nova%s"%c, host_name=i)
#     c += 1



#==================R153===================#

# list = ["r153-dell-compute-0.r153.nfv.lab", "r153-dell-compute-1.r153.nfv.lab", "r153-dell-compute-2.r153.nfv.lab"]
# c = 0
# for i in list:
#     obj.os_aggregate_creation_and_add_host(logger, conn, "nova%s"%c, availablity_zone="nova%s"%c, host_name=i)
#     c += 1


#==================r154===================#

# list = ["r154-dell-compute-0.r154.nfv.lab",
#     "r154-dell-compute-1.r154.nfv.lab", "r154-dell-compute-2.r154.nfv.lab"]
# c = 0
# for i in list:
#     obj.os_aggregate_creation_and_add_host(logger, conn, "nova%s"%c, availablity_zone="nova%s"%c, host_name=i)
#     c += 1

# ==================r8===================#

# list = ["r8-14g-dell-compute-0.oss.labs",
#     "r8-14g-dell-compute-1.oss.labs", "r8-14g-dell-compute-2.oss.labs"]
# c = 0
# for i in list:
#     obj.os_aggregate_creation_and_add_host(logger, conn, "nova%s"%c, availablity_zone="nova%s"%c, host_name=i)
#     c += 1



# os.system("openstack aggregate list")
# os.system("openstack flavor list")
# logger.info("Adding Security Group Rules")

# obj.os_sec_group_n_rules_creation(logger, conn, data["static_secgroup"], "Secgroup for icmp,tcp,udp", ["tcp", "icmp", "udp"], "0.0.0.0/0")

# logger.info("Creating Keypair and setting permission")
#
# os.system("openstack keypair create ssh-key > /home/osp_admin/ssh-key.pem")
# os.system("chmod 400 /home/osp_admin/ssh-key.pem")
# os.system("openstack keypair list")
# # obj.os_flavor_creation(logger, conn, "legacy_flavor", 2048, 2, 20)
# # obj.os_flavor_sriov_creation(logger, conn, "sriov_flavor", 1024, 2, 40)
# # obj.os_image_creation(logger, conn, data["static_image"], data["static_image_path"],data["static_image_format"],"bare")
#
net_info = obj.os_network_creation(logger, conn, data["static_network"], data["static_cidr"], data["static_subnet"], data["static_gateway"])
#,provider_dic={ 'network_type': 'vlan','physical_network' : 'physint', 'segmentation_id': 205 })
logger.info(net_info)
os.system("openstack network list")
# os.system("openstack network show %s" %data["static_network"])
# pdb.set_trace()
# net_data=str(net_info)
# seg_id= net_data.split(",")[11].strip()
# segmentation_id=seg_id.split("=")[1].strip()
# logger.info(seg_id)
# logger.info(segmentation_id)
# # obj.os_flavor_ovsdpdk_creation(logger, conn, data["ovsdpdk_flavor"], 1024, 2, 40)
# # os.system("openstack keypair list")
obj.os_router_creation(logger, conn, data["static_router"], data["static_port"], data["static_network"])
# obj.os_server_creation(logger, conn, data["server_name"], data["static_flavor"], data["static_image"], data["static_network"], data["static_secgroup"], data["zone1"], data["key_name"], 1, 3)
# obj.os_keypair_creation_with_key_file(logger, conn, data["key_name"], data["key_file_path"])

delete_object = Os_Deletion_Modules()
conn_delete = delete_object.os_connection_creation()


#================Creating Aggregate and Zones=====================#
#================Key Pair Creation========================#
# os.system("openstack keypair create dpdk-key > dpdk-key.pem")
# os.system("openstack keypair create sriov-key > sriov-key.pem")
# os.system("openstack keypair create dvr-key > dvr-key.pem")
# os.system("openstack keypair create static-key > static-key.pem")


# os.system("openstack flavor create dpdk-flavor --ram 4096 --disk 30 --vcpus 4")
# os.system("openstack flavor set --property hw:cpu_policy=dedicated --property hw:mem_page_size=1GB dpdk-flavor")
# os.system("openstack flavor list")
# os.system("openstack image list")




#================checking 2 compute nodes========================#
# delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete,
#                                                             "test_1", "test_2",
#                                                             "net1", "net2",
#                                                             "router",
#                                                             "port1", "port2")
# obj.create_2_instances_on_dif_compute_dif_network(logger, conn, "test_1", "test_2",
#                                                                                 "net1", "net2",
#                                                                                 "subnet1", "subnet2",
#                                                                                 "router",
#                                                                                 "port1","port2",
#                                                                                 "nova1", "nova2",
#                                                                                 "192.168.10.0/24","192.168.10.1",
#                                                                                 "192.168.20.0/24","192.168.20.1",
#                                                                                 "m1.medium", "centos",
#                                                                                 "c11a0ebb-22bb-4658-9804-c20d0053412a",
#                                                                                 assign_floating_ip=False)

# time.sleep(120)

# delete_object.delete_2_instances_and_router_with_2_networks(logger, conn_delete,
#                                                             "test_1", "test_2",
#                                                             "net1", "net2",
#                                                             "router",
#                                                             "port1", "port2")

# obj.os_create_instance_snapshot(logger, conn, "centos_snap", "centos-1", wait=True)
#
#
# os.system("openstack image list")

# obj.os_server_creation(logger, conn, "centos_snap_vm", "ceph-flavor-2", "ceph_med_vm_snap", "storage-net", "c11a0ebb-22bb-4658-9804-c20d0053412a", "nova2", "ceph-key")

# delete_object.os_delete_server(logger, conn_delete, "centos", 1, 3)
# delete_object.os_delete_server(logger, conn_delete, "centos_snap_vm", 1, 3)