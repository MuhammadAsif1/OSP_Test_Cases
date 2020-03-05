import os
import sys
from openstack import connection
import json
import pdb
import logging
import time
import subprocess
import paramiko
# import re

###############################################################################
# reading & then conversion of json file into python dictionary
json_file = "var.json"
if os.path.exists(json_file):
    try:
        with open(json_file) as data_file:
            data = json.load(data_file)

        # print(data["image_name"])
    except:
        print("Failed to load Json_File")

else:
    print("\nFile not found!!! Exception Occurred \n")

# Gets or creates a logger
logger = logging.getLogger(__name__)

# set log level, here INFO but can be changed to any Log Level
logger.setLevel(logging.INFO)

# define file handler & console handler and then set formatter
file_handler = logging.FileHandler('logfile.log')
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')  # noqa
file_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# add file and console handler to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


###############################################################################


# Functions

# Connection
def create_connection(auth_url, project_name, username, password, d_name):
    return connection.Connection(
        auth_url=auth_url,
        project_name=project_name,
        username=username,
        password=password,
        domain_name=d_name
    )


# Image Creation
def create_image_os(conn, image_name, img_file):
    logger.info("                                          ")
    logger.info("##########################################")
    logger.info("             Image Creation               ")
    logger.info("##########################################")
    logger.info("                                          ")

    logger.info("Creating Image: %s" % image_name)
    image = conn.get_image(image_name)
    if image is None:
        image = conn.create_image(
                            name=img_name,
                            filename=imag_file,
                            disk_format='qcow2',
                            container_format='bare'
                        )
        logger.info("Image: %s is successfully created" % image)
    else:
        logger.info("Image already exists with same name")

    return image


# Flavor Creation
def create_flavor_os(conn, name, ram, vcpus, disk):
    try:
        logger.info("                                          ")
        logger.info("##########################################")
        logger.info("             Flavor Creation              ")
        logger.info("##########################################")
        logger.info("                                          ")
        logger.info("Creating Flavor %s" % name)
        flavor = conn.get_flavor(name)
        if flavor is None:
            flavor = conn.create_flavor(name=name, ram=ram, vcpus=vcpus,
                                        disk=disk)
            time.sleep(5)
            logger.info("Flavor: %s is successfully created" % name)
        else:
            logger.info("Flavor already exists with the same name")

    except Exception as e:
            logger.exception("Exception occurred while creating a Flavor")

    return flavor


# Numa flavor Creation
def create_numa_flavor(conn, name, ram, vcpus, disk):
    try:
        flavor = create_flavor_os(conn=conn, name=name, ram=ram, vcpus=vcpus, disk=disk)
        f_id = flavor.id
        metadata = {
                    "hw:cpu_policy": "dedicated",
                    "hw:cpu_thread_policy": "require"
                    }
        logger.info("Setting metadata information of created flavor ...")
        flavor = conn.set_flavor_specs(str(f_id), metadata)

    except Exception as e:
        logger.exception("Exception has occurred while creating a NUMA Flavor")


# Keypair Creation
def create_keypair_os(conn, name, file_name):
    logger.info("                                          ")
    logger.info("##########################################")
    logger.info("             Keypair Creation             ")
    logger.info("##########################################")
    logger.info("                                          ")
    logger.info("Creating keypair: %s" % name)
    keypair = conn.get_keypair(name)
    if keypair is None:
        keypair = conn.create_keypair(name=name)
        logger.info("keypair: %s is created" % name)
        try:
            ssh_dir = "/home/osp_admin/usama/numa_tests/ssh_dir"
            os.mkdir(ssh_dir)
            os.chdir("/home/osp_admin/usama/numa_tests/ssh_dir")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
        with open(file_name, 'w') as f:
            f.write("%s" % keypair.private_key)
        os.chmod(file_name, 0o400)
        logger.info("private_key (.pem) is copied to 'ssh_dir'..")
    else:
        logger.info("Keypair already exists with the same name")
    return keypair


# Creation of Security Group
def create_sec_group_rule(conn, name, description):
    logger.info("                                           ")
    logger.info("###########################################")
    logger.info("        Security Group Creation            ")
    logger.info("###########################################")
    logger.info("                                           ")
    logger.info("Creating Security Group : %s" % name)
    sec_group = conn.get_security_group(name)
    if sec_group is None:
        try:
            sec_group = conn.create_security_group(name=name,
                                                   description=description)
            logger.info("Security Group: %s is successfull created" % name)
            logger.info("\nNow adding rule for 'ICMP'\n")
            add_rule1 = conn.create_security_group_rule(secgroup_name_or_id=sec_group.id,  # noqa
                                                        direction='ingress',  # noqa
                                                        remote_ip_prefix='0.0.0.0/0',  # noqa
                                                        protocol='icmp')  # noqa

            add_rule2 = conn.create_security_group_rule(secgroup_name_or_id=sec_group.id,  # noqa
                                                        direction='egress',
                                                        remote_ip_prefix='0.0.0.0/0',  # noqa
                                                        protocol='icmp')  # noqa

            logger.info("\nNow adding rule for 'SSH''\n")
            add_rule3 = conn.create_security_group_rule(secgroup_name_or_id=sec_group.id,  # noqa
                                                        protocol='tcp',
                                                        port_range_min=22,
                                                        port_range_max=22,
                                                        remote_ip_prefix='0.0.0.0/0')  # noqa

            logger.info("\nNow adding rule for 'TCP'\n")
            add_rule4 = conn.create_security_group_rule(secgroup_name_or_id=sec_group.id,  # noqa
                                                        protocol='tcp',
                                                        port_range_min=1,
                                                        port_range_max=65535)

            logger.info("All rules are successfully created")

        except Exception as e:
            logger.exception("Exception has occurred while creating Rules")

    else:
        logger.info("Security Group already exists with the same name")

    return sec_group


#  Network Creation
def create_network_os(conn, net_name, subnet_name, cidr, gateway):
    logger.info("                                          ")
    logger.info("##########################################")
    logger.info("             Network Creation             ")
    logger.info("##########################################")
    logger.info("                                          ")
    logger.info("Creating Network %s" % net_name)
    network = conn.get_network(net_name)
    if network is None:
        try:
            network = conn.create_network(name=net_name)
            n_id = network.id
            subnetwork = conn.create_subnet(network_id=n_id,
                                            cidr=cidr,
                                            name=subnet_name,
                                            ip_version="4",
                                            gateway_ip=gateway)
            logger.info("Network %s is successfully created" % net_name)

        except Exception as e:
            logger.info("Exception has occurred while creating a network")
    else:
        logger.info("Network already exists with the same name")
    return network


# Creation of NUMA Instances
def create_numa_instance(conn, server_name,
                         flavor_name, image_name,
                         network_name, secgroup_name,
                         ssh_key_name=data["pub_key"]):
    logger.info("Creating Server: %s" % server_name)
    ser_obj = conn.get_server(server_name)
    if ser_obj is None:
        try:
            logger.info("Creating Server: %s" % server_name)
            flavor = conn.get_flavor(
                     flavor_name)
            image = conn.get_image(
                    image_name)
            net = conn.get_network(
                  network_name)
            sec_gr_id = conn.get_security_group(
                        secgroup_name).id
            instance = conn.create_server(name=server_name, image=image_name,
                                          flavor=flavor_name,
                                          key_name=ssh_key_name,
                                          network=network_name,
                                          availability_zone='nova0',
                                          security_groups=sec_gr_id)

            logger.info("Please wait! While instane is up and running")
            time.sleep(10)
            logger.info("Server: %s is successfully created" % server_name)

        except Exception as e:
            logger.exception("Exception has occurred while creating a Server")
            conn.delete_server(server_name)

    else:
        logger.info("Server already exists with the same name")


# SSH into compute node
def ssh_into_compute_node(conn, command):
    try:
        user_name = "heat-admin"
        logger.info("Trying to connect with a compute node")
        # ins_id = conn.get_server(server_name).id
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_session = ssh_client.connect('192.168.120.24', username=user_name, password="")  # noqa
        logger.info("SSH Session is established")
        logger.info("Running command in a compute node")
        # pdb.set_trace()
        stdin, stdout, stderr = ssh_client.exec_command(command)
        out = stdout.read()
        print(out)
        return int(out)
    except:
        logger.info("Unable to ssh into compute node")
        # conn.delete_server(server_name)
    finally:
        ssh_client.close()
        logger.info("Connection from client has been closed")


# Test Cases Functions are Starting Here !!
# They are all will be called in main() Function
def test_case_3(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 3 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        os_flavor = create_numa_flavor(conn, name=data["numa_flavor"],
                                       ram=4096, vcpus=4, disk=40)

        os_server_1 = create_numa_instance(conn, server_name='numa3_vm',  # noqa
                                           flavor_name=data["numa_flavor"],  # noqa
                                           image_name=data["image_name"],  # noqa
                                           network_name=data["net_name"],  # noqa
                                           secgroup_name=data["sec_group_name"])  # noqa

        # pdb.set_trace()
        ins_id = conn.get_server('numa3_vm').id
        print(ins_id)
        comm = "sudo -i virsh dumpxml " + ins_id + " | grep vcpupin | awk 'NR{count++} END {print count}'"  # noqa
        server_vcpus = ssh_into_compute_node(conn, command=comm)
        print (server_vcpus)
        flavor_vcpus = conn.get_flavor(data["numa_flavor"]).vcpus
        print(flavor_vcpus)
        if server_vcpus == flavor_vcpus:
            logger.info("Test Case 3 is successfully verified")
            logger.info("vcpus pinned are same as numa flavor vcpus")

        else:
            logger.info("Test is failed, vcpus are not equal")

        logger.info("Now Cleaning up the resources for Test case 3")
        logger.info("Deleting Server")
        conn.delete_server('numa3_vm')
        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Resources are successfully deleted")

    except Exception as e:
        logger.info("Unable to run test case 3")
        logger.info("Deleting Server")
        ser = conn.get_server('numa3_vm')
        if ser is None:
            logger.info("Server doesn't exists")

        else:
            conn.delete_server('numa3_vm')
            logger.info("Server is deleted")

        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")


def test_case_5(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 5 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        os_flavor = create_numa_flavor(conn, name=data["numa_flavor"],
                                       ram=4096, vcpus=8, disk=40)

        vm_names = ["numa5_vm1", "numa5_vm2", "numa5_vm3", "numa5_vm4",
                    "numa5_vm5", "numa5_vm6", "numa5_vm7", "numa5_vm8",
                    "numa5_vm9", "numa5_vm10"]
        logger.info("Creating 10 instances using 8 vcpus flavor")
        for vm in vm_names:
            os_server = create_numa_instance(conn, server_name=vm,  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa

        try:
            logger.info("Creaing 11th instance")
            os_server = create_numa_instance(conn, server_name='numa5_vm11',  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            # logger.info("Instance 11 is successfully created")

        except Exception as e:
            logger.info("Cannot able to create Instance 11")
            logger.info("Test Case 5 is successfully verified")

        logger.info("Now Cleaning up the resources for Test case 5")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            conn.delete_server(vm)
        logger.info("Instances are successfully deleted")

        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Flavor is successfully deleted")

    except Exception as e:
        logger.info("Unable to execute test_case_5")
        logger.info("Deleting all the NUMA instances")
        for vm in vm_names:
            ser = conn.get_server(vm)
            if ser is None:
                logger.info("Server doesn't exists")
            else:
                conn.delete_server(vm)
                logger.info("Instance: %s is deleted" % vm)
        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")


def test_case_6(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 6 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        os_flavor = create_numa_flavor(conn, name=data["numa_flavor"],
                                       ram=4096, vcpus=40, disk=40)

        instances = ["numa6_vm1", "numa6_vm2"]
        logger.info("Creating 2 instances with numa flavor")
        for vm in instances:
            os_server = create_numa_instance(conn, server_name=vm,  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            logger.info("Instance: %s is Successfully created" % vm)

        try:
            logger.info("Creaing 3rd instance")
            os_server = create_numa_instance(conn, server_name='numa6_vm3',  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            logger.info("Instance 3rd is successfully created")

        except Exception as e:
            logger.info("Cannot able to create 3rd Instance")
            logger.info("Test case 6 is successfully verified")
            # logger.info("Now, Deleting 3rd Instance")
            # conn.delete_server("numa6_vm3")

        logger.info("Now Cleaning up the resources for Test case 6")
        logger.info("Deleting all the numa instances")
        for vm in instances:
            conn.delete_server(vm)
        logger.info("Instances are successfully deleted")

        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Flavor is successfully deleted")

    except Exception as e:
        logger.info("Unable to execute test_case_6")
        logger.info("Deleting all the numa instances")
        for vm in instances:
            ser = conn.get_server(vm)
            if ser is None:
                logger.info("Server doesn't exists")
            else:
                conn.delete_server(vm)
                logger.info("Instance: %s is deleted" % vm)
        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")


def test_case_7(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 7 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        logger.info("Creating NUMA flavor with 4 vcpus")
        create_numa_flavor(conn, name=data["numa_flavor"],
                           ram=4096, vcpus=4, disk=40)

        logger.info("Now creating instances using 4vcpus NUMA flavor")
        vm_names = ["numa7_vm1", "numa7_vm2"]
        for vm in vm_names:
            os_server = create_numa_instance(conn, server_name=vm,  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            logger.info("Instance: %s is Successfully created" % vm)

        vm1_id = conn.get_server('numa7_vm1')
        vm2_id = conn.get_server('numa7_vm2')
        for i in range(1, 5):
            comm_1 = "sudo -i virsh dumpxml " + vm1_id + " | grep cpuset | gawk 'FNR == " + i + " {print $2}' FPAT='[0-9]+'"  # noqa
            comm_2 = "sudo -i virsh dumpxml " + vm2_id + " | grep cpuset | gawk 'FNR == " + i + " {print $2}' FPAT='[0-9]+'"  # noqa

            output_1 = ssh_into_compute_node(conn, command=comm_1)
            output_2 = ssh_into_compute_node(conn, command=comm_2)
            if output_1 != output_2:
                logger.info("Cpus are not equal: Test is going well")

            else:
                logger.info("Cpus are equal: Test is Failed")
                logger.info("Verification of Test case 7 is failed")
                logger.info("Exiting from loop")
                break

        logger.info("Now Cleaning up the resources for Test case 7")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            conn.delete_server(vm)
            logger.info("Instance: %s is deleted" % vm)
        logger.info("Instances are successfully deleted")

        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Flavor is successfully deleted")

    except Exception as e:
        logger.info("Exception has occurred: Unable to Run Test Case 7")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            ser = conn.get_server(vm)
            if ser is None:
                logger.info("Server doesn't exists")
            else:
                conn.delete_server(vm)
                logger.info("Instance: %s is deleted" % vm)
        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")


def test_case_8(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 8 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        logger.info("Creating NUMA flavor with 4 vcpus")
        create_numa_flavor(conn, name=data["numa_flavor"],
                           ram=4096, vcpus=4, disk=40)

        logger.info("Now creating instances using 4vcpus NUMA flavor")
        vm_names = ["numa8_vm1", "numa8_vm2"]
        for vm in vm_names:
            os_server = create_numa_instance(conn, server_name=vm,  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            logger.info("Instance: %s is Successfully created" % vm)
            vm_id = conn.get_server(vm).id
            try:
                for i in range(1, 5):
                    comm = "sudo -i virsh dumpxml " + vm_id + " | grep cpuset | gawk 'FNR == " + i + " {print $2}' FPAT='[0-9]+'"  # noqa
                    output = ssh_into_compute_node(conn, command=comm)
                    if output % 2 == 0:
                        logger.info("Cpu is: %s and it is 'EVEN'" % output)

                    else:
                        logger.info("Cpu is: %s and is ODD" % output)
                        logger.info("Test Verification is failed")
                        break
            except Exception as e:
                logger.info("SSH Failed: Unable to execute commands in Compute Node for Test Verification")  # noqa

        logger.info("Now Cleaning up the resources for Test case 8")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            conn.delete_server(vm)
            logger.info("Instance: %s is deleted" % vm)
        logger.info("Instances are successfully deleted")

        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Flavor is successfully deleted")

    except Exception as e:
        logger.info("Exception has occurred: Unable to Run Test Case 8")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            ser = conn.get_server(vm)
            if ser is None:
                logger.info("Server doesn't exists")
            else:
                conn.delete_server(vm)
                logger.info("Instance: %s is deleted" % vm)
        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")

        # even_odd_comm = "sudo -i virsh dumpxml 24c4e0d7-a2a7-4d2d-9826-58877ff49da3 | grep cpuset | gawk 'FNR == 1 {print $2}' FPAT='[0-9]+'"
        # output = ssh_into_compute_node(conn, server_name='numa_vm_tc_7', flavor_name=data["numa_name"], command=comm)
        # sudo -i virsh dumpxml 24c4e0d7-a2a7-4d2d-9826-58877ff49da3 | grep cpuset | gawk ' NR<5 {print $2}' FPAT='[0-9]+'


def test_case_9(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 9 of NUMA             ")
        logger.info("##################################################")
        logger.info("                                                  ")

        logger.info("Creating NUMA flavor with 4 vcpus")
        create_numa_flavor(conn, name=data["numa_flavor"],
                           ram=4096, vcpus=8, disk=40)
        logger.info("Executing test case 9 of NUMA")
        vm_names = ["numa9_vm1", "numa9_vm2", "numa9_vm3", "numa9_vm4",
                    "numa9_vm5", "numa9_vm6", "numa9_vm7", "numa9_vm8",
                    "numa9_vm9", "numa9_vm10"]
        logger.info("Creating 10 instances using 4 vcpus flavor")
        for vm in vm_names:
            os_server = create_numa_instance(conn, server_name=vm,  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa

        # Stoping all the VMs
        for vm in vm_names:
            try:
                logger.info("Stopping all the NUMA instances")
                conn.stop_server(vm)
                logger.info("Server: %s has been stopped" % vm)

            except Exception as e:
                logger.info("Exception Occurred while stopping the instance")

        # Creating 11th Instance
        try:
            logger.info("Creaing 11th instance")
            os_server = create_numa_instance(conn, server_name='numa9_11',  # noqa
                                             flavor_name=data["numa_flavor"],  # noqa
                                             image_name=data["image_name"],  # noqa
                                             network_name=data["net_name"],  # noqa
                                             secgroup_name=data["sec_group_name"])  # noqa
            logger.info("Instance 11th is successfully created")

        except Exception as e:
            logger.info("Unable to create 11th Instance")
            logger.info("Test case 9 is successfully verified")

        logger.info("Now Cleaning up the resources for Test case 9")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            conn.delete_server(vm)
            logger.info("Instance: %s is deleted" % vm)
        logger.info("Instances are successfully deleted")

        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("Flavor is successfully deleted")

    except Exception as e:
        logger.info("Exception has occurred: Unable to Run Test Case 9")
        logger.info("Deleting all the numa instances")
        for vm in vm_names:
            ser = conn.get_server(vm)
            if ser is None:
                logger.info("Server doesn't exists")
            else:
                conn.delete_server(vm)
                logger.info("Instance: %s is deleted" % vm)

        logger.info("Deleting NUMA Flavor")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is deleted")


def test_case_10(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 10 of NUMA            ")
        logger.info("##################################################")
        logger.info("                                                  ")

        logger.info("Creating two numa Flavors for test case 10")
        flavor_1 = 'numa_f1'
        flavor_2 = 'numa_f2'
        create_numa_flavor(conn, name=flavor_1,
                           ram=4096, vcpus=4, disk=40)
        create_numa_flavor(conn, name=flavor_2,
                           ram=4096, vcpus=8, disk=40)

        logger.info("Creaing an instance from First Flavor")
        os_server = create_numa_instance(conn, server_name='numa10_vm1',  # noqa
                                         flavor_name=flavor_1,  # noqa
                                         image_name=data["image_name"],  # noqa
                                         network_name=data["net_name"],  # noqa
                                         secgroup_name=data["sec_group_name"])  # noqa
        try:
            logger.info("Resizing Server to 2nd Flavor")
            conn.resize_server(server='numa10_vm1', flavor=flavor_2)
            logger.info("Server is successfully resized")

        except Exception as e:
            logger.info("Unable to resize a server")
            logger.info("Test case 10 is successfully verified")

        logger.info("Now Cleaning up the resources for Test case 10")
        logger.info("Deleting Server")
        conn.delete_server('numa10_vm1')
        logger.info("Server is Deleted")
        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor('numa_f1')
        conn.delete_flavor('numa_f2')
        logger.info("Flavors are deleted")

    except Exception as e:
        logger.info("Unable to run Test case 10")
        logger.info("Deleting Instance")
        ser = conn.get_server('numa10_vm1')
        if ser is None:
            logger.info("Server doesn't Exists")

        else:
            conn.delete_server("numa10_vm1")

        logger.info("Deleting Flavors")
        f_1 = conn.get_flavor('numa_f1')
        if f_1 is None:
            logger.info("Flavor doesn't Exists")

        else:
            conn.delete_flavor('numa_f1')
            logger.info("Flavor is successfully deleted")

        f_2 = conn.get_flavor('numa_f2')
        if f_2 is None:
            logger.info("Flavor doesn't Exists")

        else:
            conn.delete_flavor('numa_f2')
            logger.info("Flavor is successfully deleted")


def test_case_11(conn):
    try:
        logger.info("                                                  ")
        logger.info("##################################################")
        logger.info("        Executing Test Case 11 of NUMA            ")
        logger.info("##################################################")
        logger.info("                                                  ")

        logger.info("Creating Flavor for migarated Instance")
        create_numa_flavor(conn, name=data["numa_flavor"],
                           ram=4096, vcpus=4, disk=40)

        logger.info("Now, Creating an Instance")
        os_server = create_numa_instance(conn, server_name='numa11_vm1',  # noqa
                                         flavor_name=data["numa_flavor"],  # noqa
                                         image_name=data["image_name"],  # noqa
                                         network_name=data["net_name"],  # noqa
                                         secgroup_name=data["sec_group_name"])  # noqa

        logger.info("Now migrating above created Server to another host")
        try:
            conn.live_migrate_server(server='numa11_vm1', host='r62-dell-compute-1.r62.nfv.lab')  # noqa
            logger.info("Instance is successfully migrated to Zone: 'nova1'")

        except Exception as e:
            logger.info("Instance Migration is Failed")
            logger.info("Verification of Test Case 11 is Failed")

        logger.info("Now Cleaning up the resources for Test case 11")
        logger.info("Deleting Server")
        conn.delete_server('numa11_vm1')
        logger.info("Server is Deleted")
        logger.info("Deleting NUMA Flavor")
        conn.delete_flavor(data["numa_flavor"])
        logger.info("NUMA Flavor is deleted")

    except Exception as e:
        logger.info("Exception has occurred: Unable to Run Test Case 11")
        logger.info("Deleting Instance")
        ser = conn.get_server('numa11_vm1')
        if ser is None:
            logger.info("Server doesn't Exists")

        else:
            conn.delete_server("numa11_vm1")

        logger.info("Deleting Flavors")
        flavor = conn.get_flavor(data["numa_flavor"])
        if flavor is None:
            logger.info("Flavor doesn't Exists")
        else:
            conn.delete_flavor(data["numa_flavor"])
            logger.info("Flavor is successfully deleted")


# main function
def main():

    # Setting uo the enviornment on which Test Cases will run
    conn = create_connection("http://100.67.62.61:5000//v3", "admin",
                             "admin",
                             "6uJrRbyMVn7rc3RrnfeggbKe9", "Default")
    os_image = create_image_os(conn, image_name=data["image_name"],
                               img_file="/home/osp_admin/usama/cirros-0.4.0-x86_64-disk.img")  # noqa

    os_keypair = create_keypair_os(conn, name=data["pub_key"],
                                   file_name=data["pr_pem_key"])
    os_private_network = create_network_os(conn, net_name=data["net_name"],
                                           subnet_name=data["sub_name"],
                                           cidr=data["cidr"],
                                           gateway=data["gateway"])

    os_sec_group = create_sec_group_rule(conn, name=data["sec_group_name"],
                                         description="ICMP_SSH_TCP_RULES")

    # NUMA Test Cases Functions Calling
    test_case_3(conn)
    test_case_5(conn)
    test_case_6(conn)
    test_case_7(conn)
    test_case_8(conn)
    test_case_9(conn)
    test_case_10(conn)
    test_case_11(conn)


if __name__ == '__main__':
    main()
    logger.info("*********************************************************************")
    logger.info("  Thankyou for using this script for Execution of NUMA Test Cases   ")
    logger.info("*********************************************************************")


