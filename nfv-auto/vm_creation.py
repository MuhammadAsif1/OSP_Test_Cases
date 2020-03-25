import os
import sys
import json
from openstack import connection
import pdb
import time
from source_R8rc import Source_Module


"""
	MODULES:
	1.Create Flavor
	2.Create KeyPair
	3.Create Security Group & Rules
	4.Create Image
	5.Create Private Network and subnetwork
	6.Create Router and Connect it to External Network
	7.Create 2 VMs from above Specs
	8.Floating IP assignment and creation
	9.SSH and ping those 2 VMs Created Above
"""

# """
# 	SETTING ENVIRONMENT VARIABLE FOR R153
# """
# os.environ["OS_NO_CACHE"]="True"
# os.environ["COMPUTE_API_VERSION"]="1.1"
# os.environ["OS_USERNAME"]="admin"
# os.environ["no_proxy"]=",100.67.153.161,192.168.120.100"
# os.environ["OS_USER_DOMAIN_NAME"]="Default"
# os.environ["OS_VOLUME_API_VERSION"]="3"
# os.environ["OS_CLOUDNAME"]="r153"
# os.environ["OS_AUTH_URL"]="http://100.67.153.61:5000//v3"
# os.environ["NOVA_VERSION"]="1.1"
# os.environ["OS_IMAGE_API_VERSION"]="2"
# os.environ["OS_PASSWORD"]="fpJwYm9yqWNZXsfaANJFPcvwC"
# os.environ["OS_PROJECT_DOMAIN_NAME"]="Default"
# os.environ["OS_IDENTITY_API_VERSION"]="3"
# os.environ["OS_PROJECT_NAME"]="admin"
# os.environ["OS_AUTH_TYPE"]="password"

global_setup_file = "setup.json"
global_stamp_file = "R60_stamp_data.json"


if os.path.exists(global_stamp_file):
    stamp_data = None
    try:
        with open(global_stamp_file) as data_file:
            stamp_data = json.load(data_file)
        stamp_data = {str(i): str(j) for i, j in stamp_data.items()}
    except:
        print("\nFAILURE!!! error in %s file!" % global_stamp_file)
else:
    print("\nFAILURE!!! %s file not found!!!\nUnable to execute sriov script\n\n" % global_stamp_file)
    exit()

if os.path.exists(global_setup_file):
    data = None
    try:
        with open(global_setup_file) as data_file:
            data = json.load(data_file)
        data = {str(i): str(j) for i, j in data.items()}
    except:
        print("\nFAILURE!!! error in %s file!" % global_setup_file)
else:
    print("\nFAILURE!!! %s file not found!!!\nUnable to execute vm_creation script\n\n" % global_setup_file)
    exit()


if os.path.exists(data["overcloud_rc_file_path"]):
    with open(data["overcloud_rc_file_path"]) as data_file:
        rc_file_cred = data_file.read()
    for line in rc_file_cred.split("\n"):
        if "OS_AUTH_URL" in str(line):
            os_auth_url = str(line.split("=")[1].strip())
        elif "OS_PASSWORD" in str(line):
            os_pass = str(line.split("=")[1].strip())
        elif "OS_PROJECT_NAME" in str(line):
            os_project_name = str(line.split("=")[1].strip())
        elif "OS_USERNAME" in str(line):
            os_username = str(line.split("=")[1].strip())
        elif "OS_PROJECT_DOMAIN_NAME" in str(line):
            os_domain_name = str(line.split("=")[1].strip())
else:
    print("\nFAILURE!!! %s file not found!!!\nUnable to execute vm_creation script\n\n" %
           data["overcloud_rc_file_path"] )
    exit()



class Os_Creation_Modules():
    """
	# Previous credentials
	conn = connection.Connection(auth_url="http://192.168.24.12:5000//v3",
								 project_name="nfv-training",
								 username="butt",
								 password="nfv",
								 domain_name="Default"
								 )
	
    conn = connection.Connection(auth_url="http://192.168.24.16:5000//v3",
                                 # project_id="e46ed922a5a94fea968bc34bdb8f409d ",
                                 project_name="admin",
                                 username="admin",
                                 password="7Ekhk2rWaaXxukVc6eBWzcbAy",
                                 # compute_api_version='1.1',
                                 domain_name="Default"
                                 )
	SETTING ENVIRONMENT VARIABLE FOR R153
	"""
# os.environ["OS_NO_CACHE"]="True"
# os.environ["COMPUTE_API_VERSION"]="1.1"
# os.environ["OS_USERNAME"]="admin"
# os.environ["no_proxy"]=",100.67.153.61,192.168.120.100"
# os.environ["OS_USER_DOMAIN_NAME"]="Default"
# os.environ["OS_VOLUME_API_VERSION"]="3"
# os.environ["OS_CLOUDNAME"]="r153"
# os.environ["OS_AUTH_URL"]="http://100.67.153.61:5000//v3"
# os.environ["NOVA_VERSION"]="1.1"
# os.environ["OS_IMAGE_API_VERSION"]="2"
# os.environ["OS_PASSWORD"]="ZPVHzhXVKU3EDxcYrcfPCnThr"
# os.environ["OS_PROJECT_DOMAIN_NAME"]="Default"
# os.environ["OS_IDENTITY_API_VERSION"]="3"
# os.environ["OS_PROJECT_NAME"]="admin"
# os.environ["OS_AUTH_TYPE"]="password"
	
    # Openstack Connection Object Creation
    def os_connection_creation(self):
        conn = connection.Connection(auth_url=os_auth_url,
                                 project_name=os_project_name,
                                 username=os_username,
                                 password=os_pass,
                                 domain_name=os_domain_name)
        return conn


    # checking if the server/network/router/image is present in list
    def check_component_in_list(self, logger, conn, component_list_name, component_name):
        try:
            logger.info("Checking if %s: %s is present in %s list.." % (component_list_name, component_name,
                                                                  component_list_name))
            munches = None
            if "server" in component_list_name:
                munches = conn.list_servers()
            elif "network" in component_list_name:
                munches = conn.list_networks()
            elif "router" in component_list_name:
                munches = conn.list_routers()
            elif "image" in component_list_name:
                munches = conn.list_images()
            else:
                logger.info("Unable to find Component list name: %s" % component_list_name)
            found_flag = 0
            if munches is not None:
                for munch in munches:
                    if str(munch.name) == component_name:
                        logger.info("Found!")
                        found_flag = 1
                    else:
                        pass
            else:
                pass
            return found_flag
        except:
            logger.info("\nUnable to check component: %s in list: %s" %(component_name, component_list_name))
            logger.info("Error: " + str(sys.exc_info()[0]))
            logger.info("Cause: " + str(sys.exc_info()[1]))
            logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    #print "MODULE#	1 FLAVOR CEREATION"
    def os_flavor_creation(self, logger, conn, name, ram, vcpus, disk):
        logger.info ("Creating Flavor : %s" %name )
        flavor = conn.get_flavor(name)
        if flavor is None:
            flavor = conn.create_flavor(name=name, ram=ram, vcpus=vcpus, disk=disk)
        else:
            logger.info("Flavor already exists with the same name.")
        return flavor


    def os_flavor_ovsdpdk_creation(self, logger, conn, name, ram, vcpus, disk):
        try:
            flavor = conn.get_flavor(name)
            if flavor is None:
                flavor = self.os_flavor_creation(logger, conn, name, ram, vcpus, disk)
                f_id = flavor.id
                metadata = {
                        'hw:cpu_policy': 'dedicated', 'hw:cpu_thread_policy': 'require',
                        'hw:mem_page_size': 'large', 'hw:numa_nodes': '1', 'hw:numa_mempolicy': 'preferred'
                }
                logger.info("Setting metadata..")
                flavor = conn.set_flavor_specs(str(f_id), metadata)
            else:
                logger.info("Flavor already exists with the same name.")
            return flavor
        except:
            logger.info("\nUnable to create OVS-DPDK flavor!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    def os_flavor_sriov_creation(self, logger, conn, name, ram, vcpus, disk):
        try:
            flavor = conn.get_flavor(name)
            if flavor is None:
                flavor = self.os_flavor_creation(logger, conn, name, ram, vcpus, disk)
                f_id = flavor.id
                metadata = {
                        'hw:cpu_policy': 'dedicated', 'hw:mem_page_size': '1GB'
                }
                logger.info("Setting metadata..")
                flavor = conn.set_flavor_specs(str(f_id), metadata)
            else:
                logger.info("Flavor already exists with the same name.")
            return flavor
        except:
            logger.info("\nUnable to create OVS-DPDK flavor!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    #print "MODULE#  2 KEYPAIR CEREATION"
    def os_keypair_creation(self, logger, conn , name, public_key=None):
        logger.info ("Creating Keypair: %s" % name)
        keypair = conn.get_keypair(name)
        if keypair is None:
            keypair = conn.create_keypair(name=name)
        else:
            logger.info("Keypair already exists with the same name.")
        return keypair

    #Key Pair Creation and saving it using a .pem file
    def os_keypair_creation_with_key_file(self, logger, conn, name, file_name):
        logger.info ("Creating Keypair: %s" % name)
        keypair = conn.get_keypair(name)
        if keypair is None:
            keypair = os.system("openstack keypair create %s --private-key %s" % (name, file_name))
        else:
            logger.info("Keypair already exists with the same name.")
        return keypair


    #print "MODULE#  3 SECURITY GROUP AND RULES CREATION"
    def os_sec_group_rule_creation(self, logger, conn, name, desc, proto1, proto2, remote_ip):
        logger.info ("Creating Security Group : %s" %name )
        sec_group = conn.get_security_group(name)
        if sec_group is None:
            sec_group= conn.create_security_group(name=name, description=desc)
            logger.info("Adding rule for: %s" % proto1)
            add_rule1=conn.create_security_group_rule( secgroup_name_or_id=name,
                                                       protocol=proto1,
                                                       remote_ip_prefix=remote_ip
                                                       )
            logger.info("Adding rule for: %s" % proto2)
            add_rule2=conn.create_security_group_rule(
                                                        secgroup_name_or_id=name,
                                                        protocol=proto2,
                                                        remote_ip_prefix=remote_ip
                                                    )
        else:
            logger.info("Security Group already exists with the same name.")
        return sec_group

    def os_sec_group_n_rules_creation(self, logger, conn, name, desc, protocol_list, remote_ip, default_bool=True):
        logger.info ("Creating Security Group : %s" % name)
        sec_group = conn.get_security_group(name)
        if sec_group is None:
            sec_group = conn.create_security_group(name=name, description=desc)
        else:
            if default_bool:
                for protocol in protocol_list:
                    for dir in ['ingress', 'egress']:
                        logger.info("Adding rule for: %s, %s" % (protocol, dir))
                        add_rule = conn.create_security_group_rule(
                                                            secgroup_name_or_id=name,
                                                            protocol=protocol,
                                                            remote_ip_prefix=remote_ip,
                                                            direction=dir
                                                            )
            else:
                logger.info("Security Group already exists with the same name.")
        return sec_group


    #print "MODULE# 4 IMAGE CEREATION"
    def os_image_creation(self, logger, conn, img_name, imag_file, dis_f, cont_f):
        logger.info ("Creating Image : %s" % img_name)
        image = conn.get_image(img_name)
        if image is None:
            image=conn.create_image(
                            name=img_name,
                            filename=imag_file,
                            disk_format=dis_f,
                            container_format=cont_f
                        )
        else:
            logger.info("Image already exists with the same name.")
        return image


    # print "MODULE# 8 FLOATING IP ASSIGNMENT AND CREATION"
    def os_floating_ip_creation_assignment(self, logger, conn, server_name):
        logger.info ("Creating & Assigning Floating IP..")
        ser_obj=conn.get_server(name_or_id=server_name)
        pub_id=conn.get_network(data["public_network"], filters=None).id
        floating_ip_munch=conn.create_floating_ip(
                                            network=pub_id,
                                            server=ser_obj,
                                            fixed_address=ser_obj.accessIPv4#private_v4
                                        )
        return floating_ip_munch

    def os_floating_ip_creation(self, logger, conn):
        logger.info ("Creating Floating IP..")
        pub_id=conn.get_network(data["public_network"], filters=None).id
        floating_ip_munch=conn.create_floating_ip(
                                            network=pub_id
                                        )
        return floating_ip_munch

    # CREATING ZONE
    def os_zone_creation(self, logger,conn, name):
        logger.info("Creating Zone: %s" % zone)
        zone = conn.get_zone(name)
        if zone is None:
            zone = conn.create_zone(name)
        else:
            logger.info("Zone already exists with the same name.")
        return zone

    # CREATING AGGREGATE AND ADDING HOST
    def os_aggregate_creation_and_add_host(self, logger, conn, name, availablity_zone, host_name):
        logger.info ("Creating Aggregrate : %s" % name)
        aggregate = conn.get_aggregate(name)
        if aggregate is None:
            aggregate = conn.create_aggregate(name, availability_zone=availablity_zone)
            logger.info("Adding host : %s to aggregate." % host_name)
            conn.add_host_to_aggregate(name, host_name)
        else:
            logger.info("Aggregate already exists with the same name.")
        return aggregate

    # CREATING VOLUME
    def os_create_volume(self, logger, conn, size, name, image):
        logger.info ("Creating Volume : %s" % volume)
        volume = conn.get_volume(name)
        if volume is None:
            volume = conn.create_volume(size=size,name=name, wait=True, bootable=True,image=image)
        else:
            logger.info("Volume already exists with the same name.")
        return volume


    # CREATING VOLUME SNAPSHOT
    def os_create_volume_snapshot(self, logger, conn, name, volume_name_to_be_attached, force=True, wait=True):
        logger.info ("Creating Volume Snapshot: %s" %name)
        volume_id = conn.get_volume(name_or_id=volume_name_to_be_attached, filters=None).id
        volume_snap = conn.get_volume_snapshot(name)
        if volume_snap is None:
            volume_snap = conn.create_volume_snapshot(name=name, volume_id=volume_id,force=force,wait=wait)
        else:
            logger.info("Volume Snapshot already exists with the same name.")
        return volume_snap

    # CREATING IMAGE SNAPSHOT (FOR INSTANCE)
    def os_create_instance_snapshot(self, logger, conn, name, server_name, wait=True):
        logger.info ("Creating Instance Snapshot: %s" %name)
        server_id = conn.get_server(name_or_id=server_name, filters=None).id
        instance_snap = conn.get_image(name)
        if instance_snap is None:
            instance_snap = conn.create_image_snapshot(name=name, server=server_id,wait=wait)
        else:
            logger.info("Instance Snapshot already exists with the same name.")
        return instance_snap


    # ATTACH VOLUME
    def os_attach_volume(self, logger, conn, server, volume):
        logger.info ("Attaching Volume: %s to Instance: %s")
        servr = conn.get_server(name_or_id=server)
        volum = conn.get_volume(name_or_id=volume, filters=None)
        volume_att = conn.attach_volume(servr,volum, wait=True)
        return volume_att


    # DETACH VOLUME
    def os_detach_volume(self, logger, conn, server, volume):
        logger.info ("Detaching Volume..")
        servr = conn.get_server(name_or_id=server)
        volum = conn.get_volume(name_or_id=volume, filters=None)
        volume_det = conn.detach_volume(servr,volum, wait=True)
        return volume_det


    def reboot_vm(self, logger, conn, server_name):
        state = conn.set_machine_power_reboot(name_or_id=server_name)
        return state


    #logger.info("MODULE# 5 NETWORK CEREATION"
    def os_network_creation(self, logger, conn, net_name, cidr, subnet_name, gatewy, provider_dic=None):
        logger.info ("Creating Network: %s" % net_name)
        network = conn.get_network(net_name)
        if network is None:
            if provider_dic:
                network = conn.network.create_network(name=net_name, provider=provider_dic)
            else:
                network = conn.network.create_network(name=net_name)
            n_id = network.id
            subnetwork=conn.network.create_subnet(
                                                    network_id=n_id,
                                                    cidr=cidr,
                                                    name=subnet_name,
                                                    ip_version="4",
                                                    gateway_ip=gatewy
                                                )
        else:
            logger.info("Network already exists with the same name.")
        return network


    # Creating SRIOV enabled Network
    def os_create_sriov_enabled_network(self, logger, conn, network_name,  port_name,
                                        subnet_name=None, cidr=None, gateway=None,
                                        network_bool=False, subnet_bool=False, port_bool=False
                                        ):
        try:
            network = conn.get_network(network_name)
            if network is None:
                logger.info("Creating Sriov Enabled Network: %s"%network_name)
                provider_dic = {'network_type': 'vlan', 'physical_network': 'physint'}
                if network_bool:
                    network = conn.network.create_network(name=network_name, provider=provider_dic)
            else:
                logger.info("Network already exists with the same name.")

            n_id = network.id
            if subnet_bool:
                logger.info("Creating Sriov Enabled SubNet: %s" % subnet_name)
                subnetwork = conn.network.create_subnet(
                                                                network_id=n_id,
                                                                cidr=cidr,
                                                                name=subnet_name,
                                                                ip_version="4",
                                                                gateway_ip=gateway
                                                            )
            # subnet_id="c0b4d175-8db4-4782-9013-9a068d890a51"
            # net_id = net.id
            # pdb.set_trace()
            subnet_id = conn.get_network(name_or_id=network_name).subnets[0]
            if port_bool:
                logger.info("Creating Sriov Enabled Port: %s" % port_name)
                port = conn.network.create_port(
                    network_id=n_id,
                    name=port_name,
                    subnet_id=subnet_id,
                    binding_vnic_type="direct"
                )

            port = conn.get_port(name_or_id=port_name)
            p_id = port.id
            p_ip = port["fixed_ips"][0]["ip_address"]
            return [n_id, subnet_id, p_id, p_ip]

        except:
            logger.info("\nUnable to create sriov network / subnet / port.")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    #Creating Sriov offload enabled network
    def os_create_sriov_offload_enabled_network(self, logger, conn, network_name,  port_name,
                                        subnet_name=None, cidr=None, gateway=None,
                                        network_bool=False, subnet_bool=False, port_bool=False
                                        ):
        try:
            network = conn.get_network(network_name)
            if network is None:
                logger.info("Creating Sriov Offload Enabled Network: %s"%network_name)
                provider_dic = {'network_type': 'vlan', 'physical_network': 'physint'}
                if network_bool:
                    network = conn.network.create_network(name=network_name, provider=provider_dic)
            else:
                logger.info("Network already exists with the same name.")

            n_id = network.id
            if subnet_bool:
                logger.info("Creating Sriov Offload Enabled SubNet: %s" % subnet_name)
                subnetwork = conn.network.create_subnet(
                                                                network_id=n_id,
                                                                cidr=cidr,
                                                                name=subnet_name,
                                                                ip_version="4",
                                                                gateway_ip=gateway
                                                            )
            # subnet_id="c0b4d175-8db4-4782-9013-9a068d890a51"
            # net_id = net.id
            # pdb.set_trace()
            subnet_id = conn.get_network(name_or_id=network_name).subnets[0]
            if port_bool:
                logger.info("Creating Sriov Offload Enabled Port: %s" % port_name)
                port = conn.network.create_port(
                    network_id=n_id,
                    name=port_name,
                    subnet_id=subnet_id,
                    binding_vnic_type="direct"
                )

            logger.info("Setting Switchdev Capabilities to Port: %s" % port_name)
            port = os.system("openstack port set --binding-profile '{\"capabilities\": [\"switchdev\"]}' %s" % port_name)
            port = conn.get_port(name_or_id=port_name)
            p_id = port.id
            p_ip = port["fixed_ips"][0]["ip_address"]
            return [n_id, subnet_id, p_id, p_ip]

        except:
            logger.info("\nUnable to create sriov network / subnet / port.")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # Creating Network by specifying Network Provider
    def os_network_creation_with_network_provider(self, logger, conn, net_name, provider_dict, cidr, dhcp_boolean,
                  allocation_pools_list_dict, subnet_name, gateway_ip, port_name, vnic_type, fixed_ips_list_dict):
        try:
            logger.info ("Creating Network by specifying Network Provider..")
            network=conn.network.create_network(name=net_name, provider = provider_dict)
            n_id=network.id
            subnetwork = conn.network.create_subnet(
                                                    network_id = n_id,
                                                    allocation_pools = allocation_pools_list_dict,
                                                    enable_dhcp = dhcp_boolean,
                                                    cidr = cidr,
                                                    name = subnet_name,
                                                    ip_version="4",
                                                    gateway_ip=gateway_ip
                                                )
            port = conn.network.create_port(
                                                network_id = n_id,
                                                name = port_name,
                                                vnic_type = vnic_type,
                                                fixed_ips = fixed_ips_list_dict
                                            )

            return network, port
        except:
            logger.info("\nUnable to create network with network provider.")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    #print "MODULE# 6 ROUTER CEREATION"
    def os_router_creation(self, logger, conn, router_name, port_name, net_name):
        try:
            logger.info ("Creating Router: %s" % router_name)
            pub_id=conn.get_network(data["public_network"] #, filters=None
                                    ).id
            router = conn.get_router(router_name)
            if router is None:
                router=conn.create_router(
                                name=router_name,
                                ext_gateway_net_id=pub_id
                                    )
                net_id=conn.get_network(
                                net_name,
                                filters=None
                                ).id
                port = conn.get_port(name_or_id=port_name)
                if port is None:
                    port_id=conn.create_port(
                                    network_id=net_id,
                                    name=port_name
                                )
                subnet_id=conn.get_network(
                                name_or_id=net_name
                                ).subnets[0]
                router_to_subnet=conn.add_router_interface(
                                        router=router,
                                        subnet_id=subnet_id)
            else:
                logger.info("Router already exists.")
            return router
        except:
            logger.info("\nUnable to create router!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
##########+================================================dpdk and sriov
    def os_router_creation2(self, logger, conn, router_name, port_name, net_name):
        try:
            logger.info ("Creating Router: %s" % router_name)
            pub_id=conn.get_network(data["public_network"] #, filters=None
                                    ).id
            router = conn.get_router(router_name)
            if router is None:
                router=conn.create_router(
                                name=router_name,
                                ext_gateway_net_id=pub_id
                                    )
            else:
                logger.info("Router already exists.")
            net_id=conn.get_network(
                            net_name,
                            filters=None
                            ).id
            port = conn.get_port(name_or_id=port_name)
            if port is None:
                port=conn.create_port(
                                network_id=net_id,
                                name=port_name
                            )
                subnet_id = conn.get_network(
                    name_or_id=net_name
                ).subnets[0]
                router_to_subnet = conn.add_router_interface(
                    router=router,
                    subnet_id=subnet_id)
            else:
                logger.info("Port already exists.")
            return router
        except:
            logger.info("Unable to create router!")
            logger.info ("\nError: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # ROUTER CEREATION WITH 2 NETWORKS
    def os_router_creation_with_2_networks(self, logger, conn, router_name, port1_name, port2_name, net1_name, net2_name):
        try:
            logger.info ("Creating Router: %s" % router_name)
            pub_id = conn.get_network(data["public_network"]  # , filters=None
                                      ).id
            router = conn.get_router(router_name)
            if router is None:
                router = conn.create_router(
                    name=router_name,
                    ext_gateway_net_id=pub_id)
                net1_id = conn.get_network(
                    net1_name,
                    filters=None).id
                net2_id = conn.get_network(
                    net2_name,
                    filters=None).id
                port1 = conn.get_port(name_or_id=port1_name)
                if port1 is None:
                    port1_id = conn.create_port(
                        network_id=net1_id,
                        name=port1_name)
                port2 = conn.get_port(name_or_id=port2_name)
                if port2 is None:
                    port2_id = conn.create_port(
                        network_id=net2_id,
                        name=port2_name)
                subnet1_id = conn.get_network(
                    name_or_id=net1_name).subnets[0]
                subnet2_id = conn.get_network(
                    name_or_id=net2_name).subnets[0]
                router_to_subnet = conn.add_router_interface(
                    router=router,
                    subnet_id=subnet1_id)
                router_to_subnet = conn.add_router_interface(
                    router=router,
                    subnet_id=subnet2_id)
            else:
                logger.info("Router already exists.")
            return router
        except:
            logger.info("\nUnable to create router with two networks!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))



    #print "MODULE# 7 SERVER CREATION"
    def os_server_creation(self, logger, conn, server_name, flavor_name, image_name, network_name, secgroup_name,
                           availability_zone, key_name=data["key_name"], min_count=1, max_count=1):
        try:
            aval_z=availability_zone
            logger.info("Creating Server: %s" % server_name)
            logger.info("Server Count: %s" % max_count)
            f_id=conn.get_flavor(
                            name_or_id=flavor_name
                            #filters=None,
                            #get_extra=False
                            ).id
            i_id=conn.get_image(
                        image_name,
                        filters=None
                        ).id
            n_id=conn.get_network(
                            network_name,
                            filters=None
                            ).id
            s_id=conn.get_security_group(
                                    secgroup_name,
                                    filters=None
                                    ).id

            server = conn.create_server(
                    name=server_name,
                    image=i_id,
                    flavor=f_id,
                    network=n_id,
                    security_groups=s_id,
                    availability_zone=aval_z,
                    key_name=key_name,
                    min_count=min_count,
                    max_count=max_count
                )
            if min_count > 1 or max_count > 1:
                time.sleep(30)
                logger.info("\nServer Created Successfully!")
            else:
                wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
                logger.info("\nServer Created Successfully!")

            server_munch = conn.get_server(name_or_id=server_name)  # .private_v4
            return server_munch
        except:
            logger.info("\nUnable to create server!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    def os_server_creation_with_floating_ip(self, logger, conn, server_name, flavor_name, image_name, network_name,
                                            secgroup_name, availability_zone, key_name=data["key_name"]):
        try:
            aval_z = availability_zone
            logger.info("Creating Server: %s" % server_name)
            f_id = conn.get_flavor(
                name_or_id=flavor_name
                # filters=None,
                # get_extra=False
            ).id
            i_id = conn.get_image(
                image_name,
                filters=None
            ).id
            n_id = conn.get_network(
                network_name,
                filters=None
            ).id
            s_id = conn.get_security_group(
                secgroup_name,
                filters=None
            ).id
            server = conn.create_server(
                name=server_name,
                image=i_id,
                flavor=f_id,
                network=n_id,
                security_groups=s_id,
                availability_zone=aval_z,
                key_name=key_name
            )
            wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
            server_ip = conn.get_server(server_name).accessIPv4
            if server_ip == '':
                server_ip = server.addresses[network_name][0]["addr"]
            else:
                server_ip = conn.get_server(server_name).accessIPv4
            f_ip_munch = self.os_floating_ip_creation_assignment(logger, conn, server_name)
            wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
            floating_ip = f_ip_munch.floating_ip_address
            if floating_ip == '':
                floating_ip = conn.get_server(server_name).accessIPv4
            elif floating_ip == '':
                floating_ip = server.addresses[network_name][1]["addr"]
            logger.info("Instance >> Fixed IP: (%s) , Floating IP: (%s)" % (
                str(server_ip), str(floating_ip)))
            return [str(server_ip), str(floating_ip)]
        except:
            logger.info("\nUnable to create server with floating IP!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # SERVER CREATION WITH BOOT VOLUME
    def os_server_creation_boot(self, logger, conn, server_name, flavor_name, network_name, secgroup_name, availability_zone,
                                boot_volume, key_name=data["key_name"]):
        try:
            aval_z=availability_zone
            logger.info("Creating Servers with boot volume..")
            f_id=conn.get_flavor(
                            name_or_id=flavor_name,
                            filters=None,
                            get_extra=False
                            ).id
            n_id=conn.get_network(
                            network_name,
                            filters=None
                            ).id
            s_id=conn.get_security_group(
                                    secgroup_name,
                                    filters=None
                                    ).id

            server=conn.create_server(
                            name=server_name,
                            flavor=f_id,
                            network=n_id,
                            security_groups=s_id,
                            availability_zone=aval_z,
                            boot_volume=boot_volume,
                            key_name=key_name
                        )
            return server
        except:
            logger.info("\nUnable to create server on boot!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    # SERVER CREATION WITH PORT
    def os_server_creation_with_port_id(self, logger, conn, flavor_name, availability_zone, image_name, port_name,
                server_name, security_group_name, key_name=data["key_name"], assign_floating_ip=True, network_name=None):
        try:
            logger.info("Creating Server with Port ID..")
            f_id = conn.get_flavor(
                name_or_id=flavor_name,
                filters=None,
                get_extra=False
            ).id
            s_id = conn.get_security_group(
                name_or_id=security_group_name,
                filters=None
            ).id
            p_id = conn.get_port(name_or_id=port_name).id
            i_id = conn.get_image(
                name_or_id=image_name,
                filters=None
            ).id

            # n_id = network_id
            # "nic <net-id=net-uuid,v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,port-id=port-uuid,auto,none"
            # pdb.set_trace()
            # nics = [{'port-id': p_id}]
            # fixed_ip=[port_ip]
            os.system("openstack server create --flavor %s --availability-zone %s --image %s --nic port-id=%s --key-name %s --security-group %s %s"
                               %(flavor_name, availability_zone, image_name, port_name, key_name, security_group_name, server_name))
            # server = conn.create_server(
            #     name=server_name,
            #     flavor=f_id,
            #     image = i_id,
            #     # ips = fixed_ip,
            #     nics=nics,
            #     security_groups=s_id,
            #     availability_zone=availability_zone,
            #     key_name=key_name
            # )
            time.sleep(5)
            wait = conn.wait_for_server(conn.get_server(name_or_id=server_name), auto_ip=False)
            # time.sleep(50)
            if assign_floating_ip:
                server_ip = conn.get_server(server_name).accessIPv4
                # pdb.set_trace()
                if server_ip == '':
                    if network_name is not None:
                        # pdb.set_trace()
                        server_ip = conn.get_server(server_name).addresses[network_name][0]["addr"]
                    else:
                        server_ip = conn.get_server(server_name).accessIPv4
                else:
                    server_ip = conn.get_server(server_name).accessIPv4
                f_ip_munch = self.os_floating_ip_creation_assignment(logger, conn, server_name)
                wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
                floating_ip = f_ip_munch.floating_ip_address
                if floating_ip == '':
                    floating_ip = conn.get_server(server_name).accessIPv4
                elif floating_ip == '':
                    floating_ip = server1.addresses[network_name][1]["addr"]
                logger.info("Instance >> Fixed IP: (%s) , Floating IP: (%s)" % (
                    str(server_ip), str(floating_ip)))
                return [str(server_ip), str(floating_ip)]
            else:
                # server_ip = conn.get_server(name_or_id=server_name).accessIPv4
                return server
        except:
            logger.info("\nUnable to create server with port id!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # =================================================SERVER CREATION FOR VLAN AWARE VM TEST CASE=======================
    # ==================================1. CREATE SERVER PARENT PORT============================================================
    def os_create_trunk_parent_port(self, logger, conn, network_name=None, port_name=None, **params):
        try:
            network = conn.network.find_network(network_name)
            if network is None:
                net = self.os_network_creation(logger, conn, network_name, cidr, subnet_name, gatewy)
            else:
                net = conn.get_network(network_name)

            n_id = net.id
            logger.info("Creating port: %s" % port_name)
            port = conn.create_port(network_id=n_id, name=port_name)
            return port
        except:
            logger.info("\nUnable to create server with port id!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # ==================================1. CREATE SERVER SUB PORT============================================================
    def os_create_trunk_sub_port(self, logger, conn, network_name=None, port_name=None, parent_mac=None, **params):
        try:
            network = conn.network.find_network(network_name)
            if network is None:
                net = self.os_network_creation(logger, conn, network_name, cidr, subnet_name, gatewy)
            else:
                net = conn.get_network(network_name)

            n_id = net.id
            logger.info("Creating port: %s" % port_name)
            port = conn.create_port(network_id=n_id, name=port_name, mac_address=parent_mac)
            return port
        except:
            logger.info("\nUnable to create server with port id!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    # ==================================2. CREATE SERVER WITH TRUNK PORT=================================================
    def os_create_server_with_trunk_port(self, logger, conn, trunk_name, flavor_name, availability_zone, image_name,
                                         parent_port_name, sub_port_name,
                                         server_name, secgroup_name, key_name=data["key_name"], segmentation_id=None,
                                         segmentation_type=None):

        parent_port_id = str(conn.get_port(name_or_id=parent_port_name).id)
        subport_id = str(conn.get_port(name_or_id=sub_port_name).id)
        # subports = [{'port-id': subport_id,
        #              'segmentation_type': segmentation_type,
        #              'segmentation_id': segmentation_id
        #              }]
        logger.info("Creating trunk: %s" % trunk_name)
        trunk = conn.network.create_trunk(port_id=parent_port_id, name=trunk_name)
        trunk = os.system("openstack network trunk set --subport port=%s,segmentation-type=%s,"
                          "segmentation-id=%s %s"%(subport_id,
                                                   segmentation_type,
                                                   segmentation_id,
                                                   trunk_name)
                          )
        logger.info("Creating server: %s" % server_name)
        server = self.os_server_creation_with_port_id(logger, conn, flavor_name, availability_zone, image_name,
                                                      port_name=parent_port_name, server_name=server_name,
                                                      security_group_name=secgroup_name, key_name=key_name,
                                                      assign_floating_ip=True)

        return server


    # def os_test_trunk_commands(self, logger, conn):
    #     tr = conn.network.trunks()
    #     print tr
    #     return tr

    # ======================================================
    # =============CREATING SRIOV ENABLED INSTANCES=========
    # ======================================================
    def os_create_sriov_enabled_instance(self, logger, conn, network_name, port_name,router_name, subnet_name, cidr, gateway,
                                        network_bool, subnet_bool, port_bool,
                                                            flavor_name,
                                                         availability_zone,
                                                         image_name,
                                                         server_name,
                                                         security_group_name,
                                                         key_name,
                                                        assign_floating_ip=True):
        network_params = self.os_create_sriov_enabled_network(logger, conn, network_name=network_name,
                                                                         port_name=port_name,
                                                                         subnet_name=subnet_name, cidr=cidr,
                                                                         gateway=gateway,
                                                                         network_bool=network_bool,
                                                                         subnet_bool=subnet_bool, port_bool=port_bool
                                                                         )

        router = self.os_router_creation(logger, conn, router_name=router_name, port_name=port_name,
                                                    net_name=network_name)

        server = self.os_server_creation_with_port_id(logger, conn, flavor_name=flavor_name,
                                                                 availability_zone=availability_zone,
                                                                 image_name=image_name,
                                                                 port_name=port_name,
                                                                 server_name=server_name,
                                                                 security_group_name=security_group_name,
                                                                 key_name=key_name,
                                                                 assign_floating_ip=assign_floating_ip,
                                                                 network_name=network_name)
        return [network_params, router, server]


    # ==============================================================
    # =============CREATING SRIOV OFFLOAD ENABLED INSTANCES=========
    # ==============================================================
    def os_create_sriov_offload_enabled_instance(self, logger, conn, network_name, port_name,router_name, subnet_name, cidr, gateway,
                                        network_bool, subnet_bool, port_bool,
                                                            flavor_name,
                                                         availability_zone,
                                                         image_name,
                                                         server_name,
                                                         security_group_name,
                                                         key_name,
                                                        assign_floating_ip=True):
        network_params = self.os_create_sriov_offload_enabled_network(logger, conn, network_name=network_name,
                                                                         port_name=port_name,
                                                                         subnet_name=subnet_name, cidr=cidr,
                                                                         gateway=gateway,
                                                                         network_bool=network_bool,
                                                                         subnet_bool=subnet_bool, port_bool=port_bool
                                                                         )

        router = self.os_router_creation(logger, conn, router_name=router_name, port_name=port_name,
                                                    net_name=network_name)

        server = self.os_server_creation_with_port_id(logger, conn, flavor_name=flavor_name,
                                                                 availability_zone=availability_zone,
                                                                 image_name=image_name,
                                                                 port_name=port_name,
                                                                 server_name=server_name,
                                                                 security_group_name=security_group_name,
                                                                 key_name=key_name,
                                                                 assign_floating_ip=assign_floating_ip,
                                                                 network_name=network_name)
        return [network_params, router, server]

    # ======================================================
    # =============CREATING VLAN AWARE INSTANCES============
    # ======================================================
    def os_create_vlan_aware_instance(self, logger, conn, parent_network, parentport_name, subport_network, subport_name,
                                      trunk_name, flavor_name, availability_zone, image_name, server_name,
                                      sec_group,
                                      segmentation_id, segmentation_type):
        parent_port = self.os_create_trunk_parent_port(logger, conn, network_name=parent_network,
                                                port_name=parentport_name)
        parent_port_mac_addr = str(parent_port.mac_address)
        sub_port = self.os_create_trunk_sub_port(logger, conn, network_name=subport_network, port_name=subport_name, parent_mac=parent_port_mac_addr)
        subport_ip = str(sub_port["fixed_ips"][0]["ip_address"])
        server = self.os_create_server_with_trunk_port(logger, conn, trunk_name, flavor_name,
                                                       availability_zone, image_name,
                                                       parent_port_name=parentport_name,
                                                       sub_port_name=subport_name,
                                                       server_name=server_name,
                                                       secgroup_name=sec_group,
                                                       segmentation_id=segmentation_id,
                                                       segmentation_type=segmentation_type)

        logger.info(server)
        time.sleep(5)
        return [parent_port, sub_port, server[1], subport_ip]

    # ======================================================
    # =============CREATING DPDK ENABELD INSTANCES==========
    # ======================================================
    def os_create_dpdk_enabled_instance(self, logger, conn, network_name, port_name, router_name, subnet_name, cidr, gateway,
                                     flavor_name,
                                     availability_zone,
                                     image_name,
                                     server_name,
                                     security_group_name
                                     ):
        net = conn.get_network(network_name)
        if net is None:
            network_params = self.os_network_creation(logger, conn, net_name=network_name,
                                                      cidr=cidr, subnet_name=subnet_name, gatewy=gateway)
        else:
            logger.info ("Network %s already Existed:"%network_name)
        router = self.os_router_creation(logger, conn, router_name=router_name, port_name=port_name,
                                         net_name=network_name)
        server = self.os_server_creation_with_floating_ip(logger, conn, server_name=server_name,
                                                          flavor_name=flavor_name,
                                                          image_name=image_name,
                                                        network_name=network_name,
                                                          secgroup_name=security_group_name,
                                                      availability_zone=availability_zone,
                                                          key_name=data["key_name"])
        return [network_params, router, server]


    # Namespace Functions
    def get_network_namespace_id(self, logger, conn, network_name):
        network_id = str(conn.get_network(network_name).id)
        namespace_id = "qdhcp-%s" % network_id
        logger.info("Namespace id : %s" % namespace_id)
        return namespace_id


    def get_router_namespace_id(self, logger, conn, router_name):
        router_id = str(conn.get_router(router_name).id)
        namespace_id = "qrouter-%s" % router_id
        logger.info("Namespace id : %s" % namespace_id)
        return namespace_id


    def get_floating_ip_namespace_id(self, logger, conn, floating_ip_id):
        namespace_id = "fip-%s" % floating_ip_id
        logger.info("Namespace id : %s" % namespace_id)
        return namespace_id

#=========================================SEEEEEEEEEEENAAARIOSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
    # Create_1_Instances_on_SAME_Compute_SAME_Network
    def create_1_instances_on_same_compute_same_network(self, logger, conn, server_name, network_name, subnet_name,
                                                        router_name, port_name, zone, cidr,
                                                        gateway_ip, flavor_name, image_name,
                                                        secgroup_name, assign_floating_ip):
        try:
            """ This function creates:
                        1 networks
                        1 subnets
                        1 routers
                        1 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            # pdb.set_trace(logger, )
            network = self.os_network_creation(logger, conn, network_name, cidr, subnet_name, gateway_ip)
            router = self.os_router_creation(logger, conn, router_name, port_name, network_name)
            # router2 = self.os_router_creation2(logger, conn, router_name, port_name, network_name)
            server = self.os_server_creation(logger, conn, server_name, flavor_name, image_name, network_name,
                                             secgroup_name, zone)
            network_id = network.id
            router_id = router.id
            server_id = server.id
            server_ip = conn.get_server(server_name).accessIPv4  # private_v4#.accessIPv4
            if assign_floating_ip:
                logger.info("Assigning floating ip to %s" % server_name)
                wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
                server_ip = conn.get_server(server_name).accessIPv4
                if server_ip == '':
                    server_ip = server.addresses[network_name][0]["addr"]
                else:
                    server_ip = conn.get_server(server_name).accessIPv4
                f_ip_munch = self.os_floating_ip_creation_assignment(logger, conn, server_name)
                wait = conn.wait_for_server(conn.get_server(server_name), auto_ip=False)
                floating_ip = f_ip_munch.floating_ip_address
                if floating_ip == '':
                    floating_ip = conn.get_server(server_name).accessIPv4
                elif floating_ip == '':
                    floating_ip = server1.addresses[network_name][1]["addr"]
                logger.info("Instance >> Fixed IP: (%s) , Floating IP: (%s)" % (
                    str(server_ip), str(floating_ip)))
                return [network_id, router_id, server_id, str(server_ip), str(floating_ip)]
            else:
                logger.info("Instance >> Fixed IP: %s" % str(server_ip))
                time.sleep(10)
                return [network_id, router_id, server_id, str(server_ip)]
        except:
            logger.info("\nUnable to create 1 instances on same compute and same network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

#=======================================================================================================================
#=====================================FOR SRIOV ENABLED INSTANCE========================================================
    #=============================================================================================================
    # SENARIO 1 Create_2_Instances_on_DIFFERENT_Compute_DIFFERENT_Network
    # def create_2_instances_on_dif_compute_dif_network(self, conn, server1_name, server2_name, network1_name,
    #                                                   network2_name, subnet1_name, subnet2_name,
    #                                                   router_name, port1_name, port2_name, zone1, zone2, cidr1,
    #                                                   gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
    #                                                   secgroup_name, assign_floating_ip,
    #                                                   key_name="static_key",
    #                                                   instance_1_type=None,
    #                                                   instance_2_type=None):
    #     print "Creating two instances on Different Compute and Different Tenant Network.."
    #     try:
    #         """ This function creates:
    #                     2 networks (if doesn't exists)
    #                     2 subnets
    #                     1 routers
    #                     2 ports
    #                     2 instances
    #             This function uses existing:
    #                     flavor
    #                     image
    #                     security group
    #                     """
    #         if instance_1_type == "sriov":
    #             network1 = self.os_create_sriov_enabled_network(conn, network_name=network1_name,
    #                                                             port_name=port1_name,
    #                                                             subnet_name=subnet1_name,
    #                                                             cidr=cidr1,
    #                                                             gateway=gateway_ip1,
    #                                                             network_bool=True,
    #                                                             subnet_bool=True,
    #                                                             port_bool=True
    #                                             )
    #         elif instance_1_type is None:
    #             network1 = self.os_network_creation(conn, network1_name, cidr1, subnet1_name, gateway_ip1)
    #         else:
    #             print "Invalid Argument instance_1_type = Unknown value %s"%instance_1_type
    #             exit()
    #
    #         if instance_2_type == "sriov":
    #             network2 = self.os_create_sriov_enabled_network(conn, network_name=network2_name,
    #                                                             port_name=port2_name,
    #                                                             subnet_name=subnet2_name,
    #                                                             cidr=cidr2,
    #                                                             gateway=gateway_ip2,
    #                                                             network_bool=True,
    #                                                             subnet_bool=True,
    #                                                             port_bool=True
    #                                             )
    #         elif instance_2_type is None:
    #             network2 = self.os_network_creation(conn, network2_name, cidr2, subnet2_name, gateway_ip2)
    #         else:
    #             print "Invalid Argument instance_2_type = Unknown value %s"%instance_2_type
    #             exit()
    #
    #
    #
    #
    #         router = self.os_router_creation_with_2_networks(logger, conn, router_name, port1_name, port2_name,
    #                                                                     network1_name, network2_name)
    #
    #         if instance_1_type == "sriov":
    #             server1 = self.os_server_creation_with_port_id(conn, flavor_name=flavor_name,
    #                                                          availability_zone=zone1,
    #                                                          image_name=image_name,
    #                                                          port_name=port1_name,
    #                                                          server_name=server1_name,
    #                                                          security_group_name=secgroup_name,
    #                                                          key_name=key_name,
    #                                                          assign_floating_ip=False)
    #         elif instance_1_type is None:
    #             server1 = self.os_server_creation(conn, server1_name, flavor_name, image_name, network1_name,
    #                                               secgroup_name, zone1, key_name=key_name)
    #         else:
    #             print "Invalid Argument instance_1_type = Unknown value %s"%instance_1_type
    #             exit()
    #         # pdb.set_trace()
    #         time.sleep(5)
    #         if instance_2_type == "sriov":
    #             server2 = self.os_server_creation_with_port_id(conn, flavor_name=flavor_name,
    #                                                          availability_zone=zone2,
    #                                                          image_name=image_name,
    #                                                          port_name=port2_name,
    #                                                          server_name=server2_name,
    #                                                          security_group_name=secgroup_name,
    #                                                          key_name=key_name,
    #                                                          assign_floating_ip=False)
    #         elif instance_2_type is None:
    #             server2 = self.os_server_creation(conn, server2_name, flavor_name, image_name, network2_name,
    #                                               secgroup_name, zone2)
    #         else:
    #             print "Invalid Argument instance_1_type = Unknown value %s"%instance_2_type
    #             exit()
    #
    #         server1_ip = server1.accessIPv4 # for local use .private_v4
    #         server2_ip = server2.accessIPv4 # for local use .private_v4
    #         if assign_floating_ip:
    #             logger.info("Assigning floating ip to %s" %server1_name)
    #             f_ip_munch1 = self.os_floating_ip_creation_assignment(conn, server1_name)
    #             logger.info("Assigning floating ip to %s" %server2_name)
    #             f_ip_munch2 = self.os_floating_ip_creation_assignment(conn, server2_name)
    #             print "Instance1 >> Fixed IP: (%s) , Floating IP: (%s)" % (
    #             str(server1_ip), str(f_ip_munch1.floating_ip_address))
    #             print "Instance2 >> Fixed IP: (%s) , Floating IP: (%s)" % (
    #             str(server2_ip), str(f_ip_munch2.floating_ip_address))
    #             wait = conn.wait_for_server(server1, auto_ip=False)
    #             wait = conn.wait_for_server(server2, auto_ip=False)
    #             # pdb.set_trace()
    #             return [str(f_ip_munch1.floating_ip_address), str(server1_ip), str(f_ip_munch2.floating_ip_address),
    #                     str(server2_ip)]
    #         else:
    #             print "Instance1 >> Fixed IP: (%s)" % str(server1_ip)
    #             logger.info("Instance2 >> Fixed IP: (%s)" % str(server2_ip))
    #             wait = conn.wait_for_server(server1, auto_ip=False)
    #             wait = conn.wait_for_server(server2, auto_ip=False)
    #             return [str(server1_ip), str(server2_ip)]
    #     except:
    #         logger.info("Unable to create 2 instances on different compute and different network"
    #         print ("\nError: " + str(sys.exc_info()[0]))
    #         print ("Cause: " + str(sys.exc_info()[1]))
    #         print ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    def ip_assignment_printing(self, logger, conn, server1_name, server2_name, network1_name,
                                    network2_name, server1_ip, server2_ip):
        logger.info("Assigning floating ip to %s" % server1_name)
        wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
        if server1_ip == '':
            server1_ip = conn.get_server(server1_name).addresses[network1_name][0]["addr"]
        else:
            server1_ip = conn.get_server(server1_name).accessIPv4
        f_ip_munch1 = self.os_floating_ip_creation_assignment(logger, conn, server1_name)
        wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
        logger.info("Assigning floating ip to %s" % server2_name)
        wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
        if server2_ip == '':
            server2_ip = conn.get_server(server2_name).addresses[network2_name][0]["addr"]
        else:
            server2_ip = conn.get_server(server2_name).accessIPv4
        f_ip_munch2 = self.os_floating_ip_creation_assignment(logger, conn, server2_name)
        wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
        floating_ip1 = f_ip_munch1.floating_ip_address
        if floating_ip1 == '':
            floating_ip1 = conn.get_server(server1_name).accessIPv4
        elif floating_ip1 == '':
            floating_ip1 = conn.get_server(server1_name).addresses[network1_name][1]["addr"]
        logger.info("Instance1 >> Fixed IP: (%s) , Floating IP: (%s)" % (
            str(server1_ip), str(floating_ip1)))
        floating_ip2 = f_ip_munch2.floating_ip_address
        if floating_ip2 == '':
            floating_ip2 = conn.get_server(server2_name).accessIPv4
        elif floating_ip2 == '':
            floating_ip2 = conn.get_server(server1_name).addresses[network2_name][1]["addr"]
        logger.info("Instance2 >> Fixed IP: (%s) , Floating IP: (%s)" % (
            str(server2_ip), str(floating_ip2)))
        wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
        wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
        return [str(floating_ip1), str(server1_ip),
                str(floating_ip2), str(server2_ip)]


    # SENARIO 1 Create_2_Instances_on_DIFFERENT_Compute_DIFFERENT_Network
    def create_2_instances_on_dif_compute_dif_network(self, logger, conn, server1_name, server2_name, network1_name,
                                                       network2_name, subnet1_name, subnet2_name,
                                                      router_name, port1_name, port2_name, zone1, zone2, cidr1,
                                                      gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip):
        try:
            """ This function creates:
                        2 networks
                        2 subnets
                        2 routers
                        2 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info("Creating two instances on Same Compute and on Different Tenant Network..")
            network1 = self.os_network_creation(logger, conn, network1_name, cidr1, subnet1_name, gateway_ip1)
            network2 = self.os_network_creation(logger, conn, network2_name, cidr2, subnet2_name, gateway_ip2)
            router = self.os_router_creation_with_2_networks(logger, conn, router_name, port1_name, port2_name,
                                                                        network1_name, network2_name)
            server1 = self.os_server_creation(logger, conn, server1_name, flavor_name, image_name, network1_name,
                                                         secgroup_name, zone1)
            server2 = self.os_server_creation(logger, conn, server2_name, flavor_name, image_name, network2_name,
                                                         secgroup_name, zone2)
            server1_ip = str(server1.accessIPv4) # for local use .private_v4
            server2_ip = str(server2.accessIPv4) # for local use .private_v4
            if assign_floating_ip:
                ip_assignments = self.ip_assignment_printing(logger, conn, server1_name=server1_name,
                                                             server2_name=server2_name,
                                                             network1_name=network1_name,
                                                             network2_name=network2_name,
                                                             server1_ip=server1_ip,
                                                             server2_ip=server2_ip)
                return [ip_assignments[0], ip_assignments[1], ip_assignments[2], ip_assignments[3]]
            else:
                logger.info("Instance1 >> Fixed IP: (%s)" % str(server1_ip))
                logger.info("Instance2 >> Fixed IP: (%s)" % str(server2_ip))
                wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
                wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
                return [str(server1_ip), str(server2_ip)]
        except:
            logger.info("\nUnable to create 2 instances on different compute and different network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # SENARIO 2 Create_2_Instances_on_SAME_Compute_SAME_Network
    def create_2_instances_on_same_compute_same_network(self, logger, conn, server1_name, server2_name, network_name,
                                                        subnet_name,
                                                      router_name, port_name, zone, cidr,
                                                      gateway_ip, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip):
        try:
            """ This function creates:
                        1 networks
                        1 subnets
                        1 routers
                        1 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info("Creating two instances on Same Compute and Same Tenant Network..")
            network = self.os_network_creation(logger, conn, network_name, cidr, subnet_name, gateway_ip)
            router = self.os_router_creation(logger, conn, router_name, port_name, network_name)
            server1 = self.os_server_creation(logger, conn, server1_name, flavor_name, image_name, network_name,
                                                         secgroup_name, zone)
            server2 = self.os_server_creation(logger, conn, server2_name, flavor_name, image_name, network_name,
                                                         secgroup_name, zone)
            server1_ip = server1.accessIPv4 # for local use .private_v4
            server2_ip = server2.accessIPv4 # for local use .private_v4
            if assign_floating_ip:
                ip_assignments = self.ip_assignment_printing(logger, conn, server1_name=server1_name,
                                                             server2_name=server2_name,
                                                             network1_name=network_name,
                                                             network2_name=network_name,
                                                             server1_ip=server1_ip,
                                                             server2_ip=server2_ip)
                return [ip_assignments[0], ip_assignments[1], ip_assignments[2], ip_assignments[3]]
            else:
                logger.info("Instance1 >> Fixed IP: (%s)" % str(server1_ip))
                logger.info("Instance2 >> Fixed IP: (%s)" % str(server2_ip))
                wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
                wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
                return [str(server1_ip), str(server2_ip)]
        except:
            logger.info("\nUnable to create 2 instances on same compute and same network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # SENARIO 3 Create_2_Instances_on_DIFFERNET_Compute_SAME_Network
    def create_2_instances_on_dif_compute_same_network(self, logger, conn, server1_name, server2_name, network_name,
                                                       subnet_name,
                                                      router_name, port_name, zone1 ,zone2, cidr,
                                                      gateway_ip, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip):
        try:
            """ This function creates:
                        1 networks
                        1 subnets
                        1 routers
                        1 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info( "Creating two instances on Different Compute and Same Tenant Network..")
            network = self.os_network_creation(logger, conn, network_name, cidr, subnet_name, gateway_ip)
            router = self.os_router_creation(logger, conn, router_name, port_name, network_name)
            server1 = self.os_server_creation(logger, conn, server1_name, flavor_name, image_name, network_name,
                                                         secgroup_name, zone1)
            server2 = self.os_server_creation(logger, conn, server2_name, flavor_name, image_name, network_name,
                                                         secgroup_name, zone2)
            server1_ip = server1.accessIPv4 # for local use .private_v4
            server2_ip = server2.accessIPv4 # for local use .private_v4
            if assign_floating_ip:
                ip_assignments = self.ip_assignment_printing(logger, conn, server1_name=server1_name,
                                                             server2_name=server2_name,
                                                             network1_name=network_name,
                                                             network2_name=network_name,
                                                             server1_ip=server1_ip,
                                                             server2_ip=server2_ip)
                return [ip_assignments[0], ip_assignments[1], ip_assignments[2], ip_assignments[3]]
            else:
                logger.info("Instance1 >> Fixed IP: (%s)" % str(server1_ip))
                logger.info("Instance2 >> Fixed IP: (%s)" % str(server2_ip))
                wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
                wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
                return [str(server1_ip), str(server2_ip)]
        except:
            logger.info("\nUnable to create 2 instances on different compute and different network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))


    # SENARIO 4 Create_2_Instances_on_SAME_Compute_DIFFERENT_Network
    def create_2_instances_on_same_compute_dif_network(self, logger, conn, server1_name, server2_name, network1_name,
                                                       network2_name, subnet1_name, subnet2_name,
                                                      router_name, port1_name, port2_name, zone, cidr1,
                                                      gateway_ip1, cidr2, gateway_ip2, flavor_name, image_name,
                                                      secgroup_name, assign_floating_ip):
        try:
            """ This function creates:
                        2 networks
                        2 subnets
                        2 routers
                        2 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info("Creating two instances on Same Compute and on Different Tenant Network..")
            network1 = self.os_network_creation(logger, conn, network1_name, cidr1, subnet1_name, gateway_ip1)
            network2 = self.os_network_creation(logger, conn, network2_name, cidr2, subnet2_name, gateway_ip2)
            router = self.os_router_creation_with_2_networks(logger, conn, router_name, port1_name, port2_name,
                                                                        network1_name, network2_name)
            server1 = self.os_server_creation(logger, conn, server1_name, flavor_name, image_name, network1_name,
                                                         secgroup_name, zone)
            server2 = self.os_server_creation(logger, conn, server2_name, flavor_name, image_name, network2_name,
                                                         secgroup_name, zone)
            server1_ip = server1.accessIPv4 # for local use .private_v4
            server2_ip = server2.accessIPv4 # for local use .private_v4
            if assign_floating_ip:
                ip_assignments = self.ip_assignment_printing(logger, conn, server1_name=server1_name,
                                                             server2_name=server2_name,
                                                             network1_name=network1_name,
                                                             network2_name=network2_name,
                                                             server1_ip=server1_ip,
                                                             server2_ip=server2_ip)
                return [ip_assignments[0], ip_assignments[1], ip_assignments[2], ip_assignments[3]]
            else:
                logger.info("Instance1 >> Fixed IP: (%s)" % str(server1_ip))
                logger.info("Instance2 >> Fixed IP: (%s)" % str(server2_ip))
                wait = conn.wait_for_server(conn.get_server(server1_name), auto_ip=False)
                wait = conn.wait_for_server(conn.get_server(server2_name), auto_ip=False)
                return [str(server1_ip), str(server2_ip)]
        except:
            logger.info("\nUnable to create 2 instances on different compute and different network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

##########+===================================    VLAN AWARE    ========================================================
            # Creating 1 vlan router with parent network and subport network
    def os_vlan_router_parent_subport_network(self, logger, conn, router_name, port1_name, port2_name, net1_name,
                                              net2_name,
                                              cidr1, subnet_name1, gateway_ip1, cidr2, subnet_name2,
                                              gateway_ip2):
        try:
            p_network = self.os_network_creation(logger, conn, net_name=net1_name, cidr=cidr1,
                                                 subnet_name=subnet_name1, gatewy=gateway_ip1)
            s_network = self.os_network_creation(logger, conn, net_name=net2_name, cidr=cidr2,
                                                 subnet_name=subnet_name2, gatewy=gateway_ip2)
            vlan_router = self.os_router_creation_with_2_networks(logger, conn, router_name=router_name,
                                                                  port1_name=port1_name,
                                                                  port2_name=port2_name, net1_name=net1_name,
                                                                  net2_name=net2_name)
            return [p_network, s_network, vlan_router]
        except:
            logger.info("\nUnable to create router with two networks!")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

##================================================SRIOV SENARIOS========================================================
    # SENARIO 1 Create_2_Instances_on_SAME_Compute_SAME_Network
    def create_2_instances_sriov_enabled_on_same_compute_same_network(self, logger, conn, server1_name, server2_name, network_name,
                                                        subnet_name,
                                                      router_name, port1_name, port2_name, zone, cidr,
                                                      gateway_ip, flavor_name, image_name,
                                                      secgroup_name, key_name, assign_floating_ip):
        try:
            """ This function creates:
                        1 networks
                        1 subnets
                        1 routers
                        1 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info("Creating two instances on Same Compute and Same Tenant Network..")
            server1 = self.os_create_sriov_enabled_instance(logger, conn, network_name=network_name,
                                                  port_name=port1_name, router_name=router_name,
                                                  subnet_name=subnet_name, cidr=cidr,
                                             gateway=gateway_ip,
                                             network_bool=True, subnet_bool=True, port_bool=True,
                                             flavor_name=flavor_name,
                                             availability_zone=zone,
                                             image_name=image_name,
                                             server_name=server1_name,
                                             security_group_name=secgroup_name,
                                             key_name=key_name,
                                            assign_floating_ip=assign_floating_ip)
            server2 = self.os_create_sriov_enabled_instance(logger, conn, network_name=network_name,
                                                  port_name=port2_name, router_name=router_name,
                                                  subnet_name=subnet_name, cidr=cidr,
                                             gateway=gateway_ip,
                                             network_bool=False, subnet_bool=False, port_bool=True,
                                             flavor_name=flavor_name,
                                             availability_zone=zone,
                                             image_name=image_name,
                                             server_name=server2_name,
                                             security_group_name=secgroup_name,
                                             key_name=key_name, assign_floating_ip=assign_floating_ip)
            return [server1,server2]
        except:
            logger.info("\nUnable to create 2 instances on same compute and same network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

    # SENARIO 2 Create_2_Instances_on_DIFF_Compute_SAME_Network
    def create_2_instances_sriov_enabled_on_diff_compute_same_network(self, logger, conn, server1_name, server2_name,
                                                                      network_name,
                                                                      subnet_name,
                                                                      router_name, port1_name, port2_name, zone1, zone2,
                                                                      cidr,
                                                                      gateway_ip, flavor_name, image_name,
                                                                      secgroup_name, key_name,
                                                                      assign_floating_ip):
        try:
            """ This function creates:
                        1 networks
                        1 subnets
                        1 routers
                        1 ports
                        2 instances
                This function uses existing:
                        flavor
                        image
                        security group 
                        """
            logger.info("Creating two instances on Same Compute and Same Tenant Network..")
            server1 = self.os_create_sriov_enabled_instance(logger, conn, network_name=network_name,
                                                            port_name=port1_name, router_name=router_name,
                                                            subnet_name=subnet_name, cidr=cidr,
                                                            gateway=gateway_ip,
                                                            network_bool=True, subnet_bool=True, port_bool=True,
                                                            flavor_name=flavor_name,
                                                            availability_zone=zone1,
                                                            image_name=image_name,
                                                            server_name=server1_name,
                                                            security_group_name=secgroup_name,
                                                            key_name=key_name,
                                                            assign_floating_ip=assign_floating_ip)
            server2 = self.os_create_sriov_enabled_instance(logger, conn, network_name=network_name,
                                                            port_name=port2_name, router_name=router_name,
                                                            subnet_name=subnet_name, cidr=cidr,
                                                            gateway=gateway_ip,
                                                            network_bool=False, subnet_bool=False,
                                                            port_bool=True,
                                                            flavor_name=flavor_name,
                                                            availability_zone=zone2,
                                                            image_name=image_name,
                                                            server_name=server2_name,
                                                            security_group_name=secgroup_name,
                                                            key_name=key_name,
                                                            assign_floating_ip=assign_floating_ip)
            return [server1, server2]
        except:
            logger.info("\nUnable to create 2 instances on same compute and same network")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

            ##================================================SRIOV OFFLOAD SENARIOS========================================================
            # SENARIO 1 Create_2_Instances_on_SAME_Compute_SAME_Network
            def create_2_instances_sriov_offload_enabled_on_same_compute_same_network(self, logger, conn, server1_name,
                                                                              server2_name, network_name,
                                                                              subnet_name,
                                                                              router_name, port1_name, port2_name, zone,
                                                                              cidr,
                                                                              gateway_ip, flavor_name, image_name,
                                                                              secgroup_name, key_name,
                                                                              assign_floating_ip):
                try:
                    """ This function creates:
                                1 networks
                                1 subnets
                                1 routers
                                1 ports
                                2 instances
                        This function uses existing:
                                flavor
                                image
                                security group 
                                """
                    logger.info("Creating two instances on Same Compute and Same Tenant Network..")
                    server1 = self.os_create_sriov_offload_enabled_instance(logger, conn, network_name=network_name,
                                                                    port_name=port1_name, router_name=router_name,
                                                                    subnet_name=subnet_name, cidr=cidr,
                                                                    gateway=gateway_ip,
                                                                    network_bool=True, subnet_bool=True, port_bool=True,
                                                                    flavor_name=flavor_name,
                                                                    availability_zone=zone,
                                                                    image_name=image_name,
                                                                    server_name=server1_name,
                                                                    security_group_name=secgroup_name,
                                                                    key_name=key_name,
                                                                    assign_floating_ip=assign_floating_ip)
                    server2 = self.os_create_sriov_offload_enabled_instance(logger, conn, network_name=network_name,
                                                                    port_name=port2_name, router_name=router_name,
                                                                    subnet_name=subnet_name, cidr=cidr,
                                                                    gateway=gateway_ip,
                                                                    network_bool=False, subnet_bool=False,
                                                                    port_bool=True,
                                                                    flavor_name=flavor_name,
                                                                    availability_zone=zone,
                                                                    image_name=image_name,
                                                                    server_name=server2_name,
                                                                    security_group_name=secgroup_name,
                                                                    key_name=key_name,
                                                                    assign_floating_ip=assign_floating_ip)
                    return [server1, server2]
                except:
                    logger.info("\nUnable to create 2 instances on same compute and same network")
                    logger.info("Error: " + str(sys.exc_info()[0]))
                    logger.info("Cause: " + str(sys.exc_info()[1]))
                    logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

            # SENARIO 2 Create_2_Instances_on_DIFF_Compute_SAME_Network
            def create_2_instances_sriov_offload_enabled_on_diff_compute_same_network(self, logger, conn, server1_name,
                                                                              server2_name,
                                                                              network_name,
                                                                              subnet_name,
                                                                              router_name, port1_name, port2_name,
                                                                              zone1, zone2,
                                                                              cidr,
                                                                              gateway_ip, flavor_name, image_name,
                                                                              secgroup_name, key_name,
                                                                              assign_floating_ip):
                try:
                    """ This function creates:
                                1 networks
                                1 subnets
                                1 routers
                                1 ports
                                2 instances
                        This function uses existing:
                                flavor
                                image
                                security group 
                                """
                    logger.info("Creating two instances on Same Compute and Same Tenant Network..")
                    server1 = self.os_create_sriov_offload_enabled_instance(logger, conn, network_name=network_name,
                                                                    port_name=port1_name, router_name=router_name,
                                                                    subnet_name=subnet_name, cidr=cidr,
                                                                    gateway=gateway_ip,
                                                                    network_bool=True, subnet_bool=True, port_bool=True,
                                                                    flavor_name=flavor_name,
                                                                    availability_zone=zone1,
                                                                    image_name=image_name,
                                                                    server_name=server1_name,
                                                                    security_group_name=secgroup_name,
                                                                    key_name=key_name,
                                                                    assign_floating_ip=assign_floating_ip)
                    server2 = self.os_create_sriov_offload_enabled_instance(logger, conn, network_name=network_name,
                                                                    port_name=port2_name, router_name=router_name,
                                                                    subnet_name=subnet_name, cidr=cidr,
                                                                    gateway=gateway_ip,
                                                                    network_bool=False, subnet_bool=False,
                                                                    port_bool=True,
                                                                    flavor_name=flavor_name,
                                                                    availability_zone=zone2,
                                                                    image_name=image_name,
                                                                    server_name=server2_name,
                                                                    security_group_name=secgroup_name,
                                                                    key_name=key_name,
                                                                    assign_floating_ip=assign_floating_ip)
                    return [server1, server2]
                except:
                    logger.info("\nUnable to create 2 instances on same compute and same network")
                    logger.info("Error: " + str(sys.exc_info()[0]))
                    logger.info("Cause: " + str(sys.exc_info()[1]))
                    logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))

                    # def os_create_server_for_ovsdpdk(self,**kwargs):
    #     fal = self.os_flavor_creation(conn, "ovsdpdk_flavor", 4096, 6, 40)
    #     f_id = fal.id
    #     metadata = {
    #                     'property': {
    #                         'hw:cpu_policy': 'dedicated', 'hw:cpu_thread_policy': 'require',
    #                                  'hw:mem_page_size': 'large', 'hw:numa_nodes': '1',
            # 'hw:numa_mempolicy': 'preferred'
    #                     }
    #     }
    #     conn_create.set_flavor_specs(f_id, metadata)
    #     server = self.os_server_creation_with_port_id(conn, server_name, flavor_name,
            # availability_zone, image_name, port_name , secgroup_name, key_name="key", assign_floating_ip=True)
    #
    # def os_server_creation_with_port_id(self, conn, server_name, flavor_name, availability_zone,
            # image_name, port_name , secgroup_name, key_name="key", assign_floating_ip=True):
    #     global server
    #     print("Creating Servers with Port ID..")
    #     f_id=conn.get_flavor(
    #                     name_or_id=flavor_name,
    #                     filters=None,
    #                     get_extra=False
    #                     ).id
    #     s_id=conn.get_security_group(
    #                             secgroup_name,
    #                             filters=None
    #                             ).id
    #     p_id = conn.get_port(name_or_id=port_name).id
    #     i_id=conn.get_image(
    #                 image_name,
    #                 filters=None
    #                 ).id
    #     server = conn.create_server(
    #                                     name=server_name,
    #                                     flavor=f_id,
    #                                     image=i_id,
    #                                     availability_zone=availability_zone,
    #                                     nics=[{'port': p_id}],
    #                                     security_groups=s_id,
    #                                     key_name=key_name)
    #     time.sleep(10)
    #     if assign_floating_ip:
    #         f_ip_munch = self.os_floating_ip_creation_assignment(logger, conn, server_name)
    #         flt_ip = f_ip_munch.floating_ip_address
    #         server_ip = conn.get_server(name_or_id=server_name).private_v4
    #         return [str(server_ip), str(flt_ip)]
    #     else:
    #         server_ip = conn.get_server(name_or_id=server_name).private_v4
    #         return str(server_ip)
    #
    #     return server




# Calling Examples:

obj=Os_Creation_Modules()
conn=obj.os_connection_creation()
# obj.create_1_instances_on_same_compute_same_network(conn, server_name="test_vm", network_name="test_net", subnet_name="test_subnet",
#                                                         router_name="test_router", port_name="test_port", zone="sriov-zone", cidr="10.0.0.0/24",
#                                                         gateway_ip="10.0.0.1", flavor_name="last", image_name="centos",
#                                                         secgroup_name="last", assign_floating_ip=True)
# obj.os_sec_group_n_rules_creation(conn, "st_secgroup", "Secgroup for icmp,tcp,udp",
# ["tcp", "icmp", "udp"], "0.0.0.0/0")
# obj.os_flavor_creation(conn, "st_flavor", 2048, 2, 20)
# obj.os_image_creation(conn,"centos","/home/osp_admin/CentOS-7-x86_64-GenericCloud-1503.qcow2","qcow2","bare")
# os.system("openstack network create public --external --provider-network-type vlan --provider-physical-network
# physext --provider-segment 38")
# os.system("openstack subnet create external_sub --network public --subnet-range 100.67.38.0/24 --allocation-pool "
#           "start=100.67.38.140,end=100.67.38.150 --gateway 100.67.38.1 --no-dhcp")
# obj.os_sec_group_rule_creation(conn,"st_secgroup","Static Security Group(tcp,icmp)", "tcp", "icmp", "0.0.0.0/0")
# obj.os_image_creation(conn,"cirros","/home/osp_admin/cirros-0.4.0-x86_64-disk.img","qcow2","bare")
# obj.os_network_creation(conn,"st_network","192.168.40.0/24","st_subnet","192.168.40.1")
# obj.os_flavor_ovsdpdk_creation(conn, "ovsdpdk_flavor", 4096, 4, 40)

# obj.os_router_creation(conn, "def_router", "def_port", "def_network")
# obj.os_server_creation(conn, "test_vm", "def_flavor", "centos", "def_network", "def_sec_grp", "nova")
# pdb.set_trace()
# conn, server_name, flavor_name, image_name, network_name, secgroup_name,
#                            availability_zone, key_name="key")
# obj.os_server_creation(conn, "test_vm1", "st_flavor", "centos", "parent_network", "st_secgroup", "nova0")
# obj.os_server_creation_boot(conn,server_name="centos_vm_bootable_vol",flavor_name="last",
# network_name="last",secgroup_name="last",availability_zone="sriov-zone",boot_volume="test_vol1")
# obj.os_floating_ip_creation_assignment(logger, conn,"vm1_last1")
# obj.os_floating_ip_creation_assignment(logger, conn,"test_vm1")
# obj.os_create_volume(conn,10,"test_vol1","centos")
# obj.os_attach_volume(conn,"centos_vm1","test_vol")
# obj.os_detach_volume(conn,"centos_vm2","test_vol")
# obj.os_create_volume_snapshot(conn,"volum_snap1","test_vol1",force=True,wait=True)

# global conn
#
# aggregrate = obj.os_create_aggregate_and_add_host(conn,"compute0.0","compute0.0","overcloud-compute-0.localdomain")
# if aggregrate:
# 	print ("Aggregate created Successfully")
# else:
# 	print ("Aggregate creation failed")
#
# os.system("openstack aggregate list")
#obj.os_ssh_ping("cirros","gocubsgo")

# list = ["r146-dell-compute-0.r146.nfv.lab", "r146-dell-compute-1.r146.nfv.lab", "r146-dell-compute-2.r146.nfv.lab"]
# c = 0
# for i in list:
#     obj.os_aggregate_creation_and_add_host(conn, "nova%s"%c, availablity_zone="nova%s"%c, host_name=i)
#     c += 1

# pdb.set_trace()
# obj.os_server_creation(conn, "test_vm", "def_flavor", "centos", "def_network", "def_sec_grp", "nova0")


# s = obj.create_2_instances_on_dif_compute_dif_network(
#               conn, server1_name=data["server1_name"], server2_name=data["server2_name"],
#                                      network1_name=data["network1_name"], network2_name=data["network2_name"],
#                                       subnet1_name=data["subnet1_name"], subnet2_name=data["subnet2_name"],
#                                       router_name=data["router_name"], port1_name=data["port1_name"],
#                                       port2_name=data["port2_name"], zone1=data["zone1"], zone2=data["zone2"],
#                                     cidr1=data["cidr1"], gateway_ip1=data["gateway_ip1"], cidr2=data["cidr2"],
#                                     gateway_ip2=data["gateway_ip2"], flavor_name=data["static_flavor"],
#                                      image_name=data["static_image"],secgroup_name=data["static_secgroup"],
#                                                       assign_floating_ip=True)

# obj=Os_Creation_Modules()
# conn=obj.os_connection_creation()
# # obj.os_vlan_router_parent_subport_network(conn, router_name="vlan_router", port1_name="parent_net_port",
# #                                           port2_name="sub_net_port", net1_name="parent_network", net2_name="sub_network",
# #                                               cidr1="192.168.80.0/24", subnet_name1="parent_subnet", gateway_ip1="192.168.80.1",
# #                                           cidr2="192.168.90.0/24", subnet_name2="sub_subnet", gateway_ip2="192.168.90.1")
# # os_server_creation()
# pdb.set_trace()
# obj.os_server_creation_with_port_id(conn, flavor_name="st_flavor", availability_zone="nova0", image_name="centos",
#                                 port_name="parent_net_port",
#                                         server_name="pagla_server", security_group_name="st_secgroup",
#                                 key_name="key", assign_floating_ip=True)

# server = conn.create_server(name="pagla2",
# flavor="st_flavor", image="centos",
# nics=[{'net-id': str(conn.get_network(name_or_id="parent_network"))},{'port-id': str(conn.get_port(name_or_id="parent_net_port").id)}],
# security_groups=["st_secgroup"],
# availability_zone="nova0",
# key_name="key")
