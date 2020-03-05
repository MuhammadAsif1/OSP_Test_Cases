#!/usr/bin/python


from openstack import connection
from paramiko import SSHClient
import sys
from source_R8rc import Source_Module

filepath=sys.argv[1]
with open(filepath) as fp:
        for line in fp:
                s = line.split()
                auth_url=s[0]
                project_name=s[1]
                username=s[2]
                password=s[3]
                domain_name=s[4]
print auth_url
print project_name
print username
print password
print domain_name

conn=connection.Connection(
							auth_url=auth_url,
							project_name=project_name,
							username=username,
							password=password,
							domain_name=domain_name
							)
print "++++++++++++++LISTING NETWORKS+++++++++++++++++++++++"

net_list=conn.list_networks()

#print net_list[0]["subnets"][0]

count=0

for t_net in net_list:
	print "Network:{}\n\t\tNetwork Name:{}\n\t\tNetwork ID:{}\n\t\tSubnet ID:{}".format(count,t_net["name"],t_net["id"],net_list[0]["subnets"][0])
	count += 1


print "Do you want to Delete a specific Network?"
choice = raw_input("Type Yes / No:	")
if choice == "Yes":
	net_del = raw_input("Enter the name of your Network you want to Delete:")
	del_network = conn.network.find_network(net_del)
        conn.delete_server(name_or_id=del_network)
        conn.delete_router(name_or_id=del_network)
      	conn.delete_port(name_or_id=del_network)

	for del_subnet in del_network.subnet_ids:
		conn.network.delete_subnet(del_subnet, ignore_missing=False)
		conn.network.delete_network(del_network, ignore_missing=False)

	print "Network {} Deleted".format(net_del)
else:
	print "No more Networks to show"

"""
net_list=conn.list_networks()
for t_net in net_list:
        print "Network:{}\n\t\tNetwork Name:{}\n\t\tNetwork ID:{}\n\t\tSubnet ID:{}".format(count,net_list[count]["name"],net_list[count]["id"],net_list[0]["subnets"][0])
        count += 1

"""

print "++++++++++++++LISTING SERVERS+++++++++++++++++++++++"

ser_list=conn.list_servers()
"""
print ser_list[0]["name"]
network_name= ser_list[0]["addresses"].keys()
print ser_list[0]["addresses"]["latest_network"][0]["addr"]
print ser_list[0]["addresses"]["latest_network"][1]["addr"]
print str(network_name[0])
"""
count=0

for t_ser in ser_list:
	network_name= t_ser["addresses"].keys()
	network_name=str(network_name[0])
        print "Server:{}\n\t\tServer Name:{}\n\t\tServer ID:{}\n\t\tPrivate IP:{}\n\t\tfloating IP:{}".format(count,t_ser["name"],t_ser["id"],t_ser["addresses"][network_name][0]["addr"],t_ser["addresses"][network_name][1]["addr"])
        count += 1

print "++++++++++++++LISTING FLAVORS+++++++++++++++++++++++"

flav_list=conn.list_flavors()
"""
print ser_list[0]["name"]
network_name= ser_list[0]["addresses"].keys()
print ser_list[0]["addresses"]["latest_network"][0]["addr"]
print ser_list[0]["addresses"]["latest_network"][1]["addr"]
print str(network_name[0])
"""
count=0
#print flav_list

for t_flav in flav_list:
#        network_name= ser_list[count]["addresses"].keys()
#        network_name=str(network_name[0])
#        print "Server:{}\n\t\tServer Name:{}\n\t\tServer ID:{}\n\t\tPrivate IP:{}\n\t\tfloating IP:{}".format(count,ser_list[count]["name"],ser_list[count]["id"],ser_list[count]["addresses"][network_name][0]["addr"],ser_list[count]["addresses"][network_name][1]["addr"])
	
        flav_names=t_flav["name"]
        print "Flavor Name:{}\t\t\tFlavor ID:{}".format(flav_names,t_flav["id"])
        count += 1

print "++++++++++++++LISTING IMAGES+++++++++++++++++++++++"

img_list=conn.list_images()
"""
print ser_list[0]["name"]
network_name= ser_list[0]["addresses"].keys()
print ser_list[0]["addresses"]["latest_network"][0]["addr"]
print ser_list[0]["addresses"]["latest_network"][1]["addr"]
print str(network_name[0])
"""
#print img_list
count=0

for t_img in img_list:
        #network_name= ser_list[count]["addresses"].keys()
        #network_name=str(network_name[0])
        #print "Server:{}\n\t\tServer Name:{}\n\t\tServer ID:{}\n\t\tPrivate IP:{}\n\t\tfloating IP:{}".format(count,ser_list[count]["name"],ser_list[count]["id"],ser_list[count]["addresses"][network_name][0]["addr"],ser_list[count]["addresses"][network_name][1]["addr"])
        img_names=t_img["name"]
	print "Image Name:{}\t\tImage ID:{}".format(img_names,t_img["id"])
	count += 1
