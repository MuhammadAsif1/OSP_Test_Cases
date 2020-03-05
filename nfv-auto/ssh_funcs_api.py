import paramiko
import time
import commands
import sys
import os
import json
import pdb
from source_R8rc import Source_Module

try:
    if os.path.exists("setup.json"):
        with open('setup.json') as data_file:
            data = json.load(data_file)
        iperf_package_path = data["iperf_package_path"]
        iperf3_package_name = data["iperf3_package_name"]
    else:
        print ("\nFAILURE!!! setup.json file not found!!!\nUnable to execute script\n\n")
        exit()
except:
    print ("\nFAILURE!!! Error in setup.json file!!!\nUnable to execute script\n\n")
    exit()


class ssh_functions():
    global ssh

    def __init__(self):
        global ssh
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()

    def start_first_session(self):
        ssh_1 = paramiko.SSHClient()
        ssh_1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_1.load_system_host_keys()
        return ssh_1

    def start_second_session(self):
        ssh_2 = paramiko.SSHClient()
        ssh_2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_2.load_system_host_keys()
        return ssh_2


    def ssh_to(self, logger, ip, username, password=None, key_file_name=None, session=None):
        try:
            if session is None:
                ssh.connect(hostname=ip, username=username, password=password, key_filename=key_file_name)
            else:
                session.connect(hostname=ip, username=username, password=password, key_filename=key_file_name)
        except paramiko.SSHException:
            logger.info("Failed to establish SSH connection with %s" %ip)


    def execute_command_return_output(self, logger, command):
        try:
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            time.sleep(1)
            output = stdout.read()
            return output
        except:
            logger.info("Error encountered while executing command: %s" % command)


    def execute_command_show_output(self, logger, command):
        try:
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
            time.sleep(1)
            for line in stdout.readlines():
                logger.info(line.strip())
        except:
            logger.info("Error encountered while executing command: %s" % command)


    def execute_command_only(self, logger, command):
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            time.sleep(1)
        except:
            logger.info("Error encountered while executing command: %s" % command)

    def check_interface_names(self, logger):
        """
            Using: | grep 'flags'
        """
        interfaces_list = []
        output = self.execute_command_return_output(logger, "sudo ifconfig | grep \"flags=\"")
        for line in output.split("\n"):
            interface_name = str(line.split(":")[0])
            if interface_name is not '':
                interfaces_list.append(interface_name)
        return interfaces_list


    def check_interface_name_and_mtu_size(self, logger):
        interface_and_mtu_size_dict = {}
        output = self.execute_command_return_output(logger, "sudo ifconfig | grep mtu")
        for line in output.split("\n"):
            try:
                interface_name = str(line.split(":")[0].strip())
                mut_size = int(line.split(":")[1].split(">")[1].replace("mtu", "").strip())
                #print "Interface: %s  mtu: %s" % (interface_name, mut_size)
                interface_and_mtu_size_dict[interface_name] = mut_size
            except:
                pass
        return interface_and_mtu_size_dict


    def ping_check_from_namespace(self, logger, namespace_id, ip_of_instance1, username_of_instance, key_file_path_of_node,
                                  ip_of_instance2, packet_size=None):
        try:
            exp_output = "5 packets transmitted, 5 received, 0% packet loss"
            for i in range(0, 3):
                if packet_size is None:
                    command = "timeout 10 sudo ip netns exec %s ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KbdInteractiveDevices=no -tti %s %s@%s \"ping -c 5 %s\"" % (
                                    namespace_id, key_file_path_of_node, username_of_instance, ip_of_instance1,
                                                                                        ip_of_instance2)
                    logger.info("Trying to ping through namespace:\nCommand: %s" % command)
                    # pdb.set_trace()
                    output = self.execute_command_return_output(logger, command)
                else:
                    command = "timeout 10 sudo ip netns exec %s ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o KbdInteractiveDevices=no -tti %s %s@%s \"ping -c 5 -s %s %s -M do\"" \
                              % (namespace_id, key_file_path_of_node, username_of_instance, ip_of_instance1, packet_size,
                                                                                                    ip_of_instance2)
                    logger.info("Trying to ping through namespace:\nCommand: %s" % command)
                    output = self.execute_command_return_output(logger, command)
                logger.info (output)
                if "Connection refused" in str(output) or "No route to host" in str(output):
                    logger.info("Retying...%s" % i)
                    time.sleep(2)
                    continue
                else:
                    break
            result = str(output)
            p_flag = False
            if exp_output in result:
                p_flag = True
            else:
                p_flag = False
            return p_flag
        except:
            self.ssh_close()
            logger.info ("\nError encountered while pinging from namespace")
            logger.info ("Error: " + str(sys.exc_info()[0]))
            logger.info ("Cause: " + str(sys.exc_info()[1]))
            logger.info ("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
            return -1


    def ping_check_with_packet_size(self, logger, ip_to_ping, packet_size):
        """
            ping to ip of node 1: ping -c 5 -s <packet size> <ip of node 1> -M do
            if expected output is seen in the ping result it returns true else false
        """
        output = self.execute_command_return_output(logger, "ping -c 5 -s %s %s -M do" % (packet_size, ip_to_ping))
        exp_output = "5 packets transmitted, 5 received, 0% packet loss"
        p_flag = 0
        logger.info(output)
        if exp_output in output:
            p_flag = 1
        else:
            p_flag = 0
        return p_flag


    def simple_ping_check(self, logger, ip_to_ping):
        """
            ping to ip of node 1: ping -c 5  <ip of node 1>
            if expected output is seen in the ping result it returns true else false
        """
        output = self.execute_command_return_output(logger, "ping -c 5 %s" % ip_to_ping)
        exp_output = "5 packets transmitted, 5 received, 0% packet loss"
        p_flag = False
        logger.info( output)
        if exp_output in output:
            p_flag = 1
        else:
            p_flag = 0
        return p_flag

    def simple_ping_check_using_inteface(self, logger, ip_to_ping, interface):
        """
            ping to ip of node 1: ping -c 5 -I <interface> <ip of node 1>
            if expected output is seen in the ping result it returns true else false
        """
        output = self.execute_command_return_output(logger, "ping -c 5 -I %s %s" % (interface, ip_to_ping))
        exp_output = "5 packets transmitted, 5 received, 0% packet loss"
        p_flag = False
        logger.info( output)
        if exp_output in output:
            p_flag = 1
        else:
            p_flag = 0
        return p_flag


    def send_key_if_not_present(self, logger, destination_path):
        key_name = destination_path.split("/")[3]
        logger.info("Checking if %s file is present.." % key_name)
        output = self.execute_command_return_output(logger, "ls")
        if key_name not in output:
            self.send_file_or_package(logger, source_path=data["key_file_path"], destination_path=destination_path)
            logger.info("Sent.")
        else:
            logger.info("Already present.")
            pass

    def send_nginx_repo_if_not_present(self, logger, destination_path):
        file_name = destination_path.split("/")[1]
        logger.info("Checking if %s file is present.." % file_name)
        output = self.execute_command_return_output(logger, "ls")
        if file_name not in output:
            self.send_file_or_package(logger, source_path=data["nginx_repo_path"], destination_path=destination_path)
            logger.info("Sent.")
        else:
            logger.info("Already present.")
            pass

    def read_remote_file(self, full_file_path):
        global ssh
        sftp_client = ssh.open_sftp()
        remote_file = sftp_client.open(full_file_path)
        file_data = remote_file.read()
        remote_file.close()
        sftp_client.close()
        return file_data

    def send_file_or_package(self, logger, source_path, destination_path):
        global ssh
        logger.info("Trying to send %s to %s..." %(source_path, destination_path))
        sftp = ssh.open_sftp()
        sftp.put(source_path, destination_path)
        time.sleep(2)
        sftp.close()

    def iperf3_initialization(self, logger, public_ip, username, key_file_path):
        self.ssh_to(logger, public_ip, username, key_file_name=key_file_path)
        output = self.execute_command_return_output(logger, "iperf3")
        if "not found" in output:
            logger.info("iperf3 is not installed on %s" %public_ip)
            self.send_and_install_iperf3_package(logger, username)
        else:
            logger.info("iperf3 is already installed on %s" %public_ip)
        self.ssh_close()

    def send_and_install_iperf3_package(self, logger, username):
        global ssh
        #output = self.locally_execute_command("timeout 5 scp -i ../key.pem /home/stack/latest-automation-code/iperf3-3.1.7-2."
        #                             "el7.x86_64.rpm %s@%s:/home/%s/" % (username, ip_of_instance, username))
        output = self.execute_command_return_output(logger, "ls ~/home/%s/"%username)
        if iperf3_package_name in str(output):
            logger.info("iperf3 package is already present.")
        else:
            logger.info("Sending iperf3 package: %s" % iperf3_package_name)
            # pdb.set_trace()
            sftp = ssh.open_sftp()
            sftp.put(iperf_package_path, '/home/%s/%s' % (username,iperf3_package_name))
            time.sleep(2)
            sftp.close()
        logger.info("Installing package...")
        logger.info(self.execute_command_return_output(logger, "timeout 10 sudo rpm -ivh /home/%s/iperf3-3.1.7-2.el7.x86_64.rpm" % username))
        return

    def execute_iperf3_s(self, logger, time=None):
        try:
            global stdout_iperf
            out = self.execute_command_return_output(logger, "pgrep iperf3")
            if out != None:
                for line in out.split("\n"):
                    if line:
                        self.execute_command_only(logger, "kill -9 %s" % (line.strip()))
            if time is None:
                stdin_u, stdout_iperf, stderr_u = ssh.exec_command("timeout 20 iperf3 -s")
            else:
                stdin_u, stdout_iperf, stderr_u = ssh.exec_command("timeout %s iperf3 -s" % (int(time)+15))
        except:
            logger.info("\nError encountered while executing iperf3 -s command for checking TCP Upload.")

    def check_bandwidth_private_ip(self, logger, username, client_ssh_ip, server_ssh_ip, client_iperf_ip, server_iperf_ip,
                                   packet_size=None, iperf_client_time=None, password=None, key_file_path=None, udp_flag=False):
        """Note: username and password of both VMs must be same.
                 Or if ssh is with key then both VMs must have the same key path."""
        try:
            # pdb.set_trace()
            bandwidth = None
            self.iperf3_initialization(logger, server_ssh_ip, username, key_file_path)
            self.iperf3_initialization(logger, client_ssh_ip, username, key_file_path)
            if udp_flag is False:
                logger.info("Checking TCP Bandwidth...")
            elif udp_flag is True:
                logger.info("Checking UDP Bandwidth...")
            self.ssh_to(logger, server_ssh_ip, username, password=password, key_file_name=key_file_path)
            ssh_2 = self.start_second_session()
            if iperf_client_time is None:
                self.execute_iperf3_s(logger)
                self.ssh_to(logger, client_ssh_ip, username, password=password, key_file_name=key_file_path, session=ssh_2)
                if packet_size is None:
                    if udp_flag is True:
                        ssh_2.exec_command("iperf3 -u -c %s -b 10G" % server_iperf_ip)
                    else:
                        ssh_2.exec_command("iperf3 -c %s" % server_iperf_ip)
                else:
                    if udp_flag is True:
                        ssh_2.exec_command("iperf3 -u -c %s -b 10 G -M %s" %(server_iperf_ip, packet_size))
                    else:
                        ssh_2.exec_command("iperf3 -c %s -M %s" %(server_iperf_ip, packet_size))
            else:
                self.execute_iperf3_s(logger, iperf_client_time)
                self.ssh_to(logger, client_ssh_ip, username, password=password, key_file_name=key_file_path, session=ssh_2)
                if packet_size is None:
                    if udp_flag is True:
                        ssh_2.exec_command("iperf3 -u -c %s -b 10G -t %s" % (server_iperf_ip, iperf_client_time))
                    else:
                        ssh_2.exec_command("iperf3 -c %s -t %s" % (server_iperf_ip, iperf_client_time))
                else:
                    if udp_flag is True:
                        ssh_2.exec_command("iperf3 -u -c %s -b 10G -M %s -t %s" % (server_iperf_ip, packet_size, iperf_client_time))
                    else:
                        ssh_2.exec_command("iperf3 -c %s -M %s -t %s" % (server_iperf_ip, packet_size, iperf_client_time))
            bandwidth = None
            for line in stdout_iperf.readlines():
                logger.info(str(line.strip()))
                if "receiver" in str(line.strip()):
                    bandwidth = ((line.split("Bytes")[1]).strip()).split("  ")[0]
            logger.info("\nBandwidth: %s\n" % bandwidth)
            ssh_2.close()
            self.ssh_close()
            return bandwidth
        except:
            self.ssh_close()
            logger.info("\nError encountered while checking bandwidth of Server: %s and Client: %s" %
                   (server_ssh_ip, client_ssh_ip))
            logger.info("\nError: " + str(sys.exc_info()[0]))
            logger.info("Cause: " + str(sys.exc_info()[1]))
            logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
            return -1

    def execute_tcp_dump(self, logger,session=None, timeout=0, interface=None, find=None):
        global stdout_a
        try:
            # print "\nExecuting tcp dump command to capture PAD packets"
            if find is None:
                stdin_a, stdout_a, stderr_a = session.exec_command("sudo timeout %s tcpdump -nnn -i %s > tcpdump.txt" %
                                                                   (timeout, interface))
            else:
                stdin_a, stdout_a, stderr_a = session.exec_command(
                    "sudo timeout %s tcpdump -nnn -i %s | grep '%s' > tcpdump.txt" %(timeout, interface, find))
        except:
            logger.info("\nError while executing tcp dump command")

#=========================================== SRIOV OFFLOAD REPRESENTOR PORT CHECK ====================================#####
    def check_ovs_offloading(self, logger, compute_ip, compute_user, instance1_ip, instance_user, key_file_path, instance2_ip, rep_port):
        """Note: username and password of both VMs must be same.
                 Or if ssh is with key then both VMs must have the same key path."""
        try:
            ssh_1 = self.start_first_session()
            ssh_2 = self.start_second_session()


            pdb.set_trace()
            self.ssh_to(logger, ip=compute_ip, username=compute_user, password=None, key_file_name=None, session=ssh_2)
            self.ssh_to(logger, ip=instance1_ip, username=instance_user, password=None, key_file_name=key_file_path, session=ssh_1)
            output = self.execute_tcp_dump(logger, session=ssh_2, timeout=120, interface=rep_port, find=None)
            stdin, stdout, stderr = ssh_1.exec_command("ping -c 30 %s" % instance2_ip, get_pty=True)
            time.sleep(1)
            logger.info("\nTcpdump output: %s\n" % output)
            ping = stdout.read()
            ssh_1.close()
            logger.info("\nPING output: %s\n" % ping)
            ssh_2.close()
            # stdin, stdout, stderr = ssh_2.exec_command("sudo tcpdump -nnn -i %s" % rep_port, get_pty=True)
            ######save output
            # time.sleep(1)
            # output_a = stdout_a.read()
            # #####show output
            # time.sleep(1)
            # for line in stdout.readlines():
            #     logger.info(line.strip())



            # for line in stdout_iperf.readlines():
            #     logger.info(str(line.strip()))
            #     if "receiver" in str(line.strip()):
            #         bandwidth = ((line.split("Bytes")[1]).strip()).split("  ")[0]
            return output
        except:
            ssh_2.close()
            ssh_1.close()
            logger.info("\nError encountered while checking ovs offload of instance2: %s and instance1: %s" %
                   (instance2_ip, instance1_ip))
            logger.info("\nError: " + str(sys.exc_info()[0]))
            logger.info("Cause: " + str(sys.exc_info()[1]))
            logger.info("Line No: %s \n" % (sys.exc_info()[2].tb_lineno))
            return output
#####################################################################################################################################################
    # def check_bandwidth_with_packet_size(self):

    def ssh_close(self):
        ssh.close()

    def locally_ping_check(self, logger, ip):
        output = commands.getstatusoutput("timeout 10 ping -c 5 %s" % ip)
        exp_output = "5 packets transmitted, 5 received, 0% packet loss"
        p_flag = False
        for line in output[1].split("\n"):
            logger.info( line.strip())
            if exp_output in str(line.strip()):
                p_flag = True
            else:
                pass
        return p_flag

    def locally_execute_command(self, command):
        output = commands.getstatusoutput(command)
        return output[1]

    # VLAN aware function
    def ssh_vlan_aware_vm(self, logger, ip_of_instance, username_of_instance, key_file_path, new_eth_file_path,
                          new_route_file_path, subport_ip, old_eth_file_path,  old_route_file_path,
                           gateway, segmentation_id, metricnumber):
        self.ssh_to(logger, ip_of_instance, username=username_of_instance, key_file_name=key_file_path)
        vm_eth_home_path = "/home/%s/ifcfg-eth0." % username_of_instance
        vm_router_home_path = "/home/%s/router-eth0."%username_of_instance
        self.send_file_or_package(logger, source_path=old_eth_file_path,
                                     destination_path=vm_eth_home_path)
        time.sleep(5)
        self.send_file_or_package(logger, source_path=old_route_file_path,
                                     destination_path=vm_router_home_path)
        time.sleep(5)
        self.execute_command_show_output(logger, "sudo cp %s %s" % (vm_eth_home_path, new_eth_file_path))
        self.execute_command_show_output(logger, "sudo cp %s %s" % (vm_router_home_path, new_route_file_path))
        self.execute_command_show_output(logger, "sudo cat %s" % new_route_file_path)
        self.execute_command_show_output(logger, "sudo cat %s" % new_eth_file_path)
        # pdb.set_trace()
        self.execute_command_show_output(logger, "sudo ls -l /etc/sysconfig/network-scripts/")
        # res = self.execute_command_show_output(logger, "sudo -i echo VLAN=yes >> /etc/sysconfig/network-scripts/ifcfg-eth0.%s"%segmentation_id)
        #####------------------------Editing Device name---------------------
        ###==========================Editing ifcfg-eth0.---- file=======================================================
        ######0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
        self.execute_command_show_output(logger,
            "sudo sed -i 's/DEVICE=\"eth0.\"/DEVICE=\"eth0.%s\"/g' %s" % (
                segmentation_id, new_eth_file_path))
        self.execute_command_show_output(logger,
            "sudo sed -i 's/IPADDR=/IPADDR=\"%s\"/g' %s" % (subport_ip, new_eth_file_path))
        ######0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0

        # =======================================================MAKING ROUTER DEFAULT FILE==============================
        ######-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0-0
        self.execute_command_show_output(logger,
            "sudo sed -i 's/gateway/%s/g' %s" % (gateway, new_route_file_path))
        self.execute_command_show_output(logger,
            "sudo sed -i 's/eth0./eth0.%s/g' %s" % (segmentation_id, new_route_file_path))
        self.execute_command_show_output(logger,
            "sudo sed -i 's/number/%s/g' %s" % (metricnumber, new_route_file_path))
        self.execute_command_show_output(logger, "sudo cat %s" % new_route_file_path)
        self.execute_command_show_output(logger, "sudo cat %s" % new_eth_file_path)
        self.execute_command_show_output(logger, "sudo ls -l /etc/sysconfig/network-scripts/")
        self.execute_command_show_output(logger, "sudo ifconfig")
        # pdb.set_trace()
        self.execute_command_show_output(logger, "sudo ifup /etc/sysconfig/network-scripts/ifcfg-eth0.%s" % segmentation_id)
        self.execute_command_show_output(logger, "sudo ifconfig")
        self.ssh_close()