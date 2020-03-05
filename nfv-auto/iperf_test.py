import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()

username = "centos"
key_file_path = "/home/stack/key.pem"
client_ssh_ip = "192.168.10.208"
server_ssh_ip = "192.168.10.204"
client_iperf_ip = "192.168.40.17"
server_iperf_ip = "192.168.40.16"

def ssh_with_key(ip, username, key_file_name):
    try:
        ssh.connect(hostname=ip, username=username, key_filename=key_file_name)
    except paramiko.SSHException:
        print ("SSH (with Key) Connection Failed. IP: %s" % ip)
        quit()


def execute_iperf3_s():
    try:
        global stdout_iperf
        stdin, stdout, stderr = ssh.exec_command("pgrep iperf3")
        for line in stdout.readlines():
            if line:
                ssh.exec_command("kill -9 %s" % (line.strip()))
        stdin_u, stdout_iperf, stderr_u = ssh.exec_command("timeout 20 iperf3 -s")
    except:
        print "iperf3 -s not executed"


global stdout_iperf
ssh_with_key(server_ssh_ip, username, key_file_path)
execute_iperf3_s()
ssh_with_key(client_ssh_ip, username, key_file_path)
ssh.exec_command("iperf3 -c %s" % server_iperf_ip)
for line in stdout_iperf.readlines():
    print line
    #if "receiver" in str(line.strip()):
    #    bandwidth = ((line.split("Bytes")[1]).strip()).split("  ")[0]
