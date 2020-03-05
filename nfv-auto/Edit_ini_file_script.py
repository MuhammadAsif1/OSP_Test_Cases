#!/usr/bin/python
# To run this script pass argument(Name of ini file)
# python script.py sample_cs.ini
import string
import os
import sys
#print "function"

def script_parameters():
   x=0
   #hpg_enable
   #numa_enable
   #ovs_dpdk_enable
   #sriov_enable
   #dvr_enable
   #octavia_enable
   #run_tempest
   #tempest_smoke_only
   #run_sanity
   print("******************************************")
   print("*           Available NFV Features       *")
   print("******************************************")
   print("*******   1-    [Huge Pages]       *******")
   print("*******   2-    [NUMA]             *******")
   print("*******   3-    [OVS-DPDK]         *******")
   print("*******   4-    [SRIOV]            *******")
   print("*******   5-    [DVR]              *******")
   print("*******   6-    [Octavia]          *******")
   print("*******   7-    [Tempest]          *******")
   print("*******   8-    [Tempest Smoke]    *******")
   print("*******   9-    [Sanity]           *******")
   print("******************************************")
   print("******************************************")
   print
   print("******************************************")
   print("* Enable/Disable Available NFV Features  *")
   print("******************************************")
   print("**********| 1 -----> Enable  |************")
   print("**********| 0 -----> Disable |************")
   print("******************************************")
   Huge_Pages = bool(input("Huge Pages : "))
   NUMA = bool(input("NUMA : "))
   OVS_DPDK = bool(input("OVS-DPDK : "))
   SRIOV = bool(input("SRIOV : "))
   DVR = bool(input("DVR : "))
   Octavia = bool(input("Octavia : "))
   Tempest = bool(input("Tempest : "))
   Tempest_smoke = bool(input("Tempest_smoke : "))
   Sanity = bool(input("Sanity : "))
   print("******************************************")
   print("******************************************")

   
   s = open(sys.argv[1],"r+")
   s1 = open("sample1.txt","w")
   for line in s.readlines():
      #print line
      x=x+1
      #Enable or Disable Huge Pages
      if (((line.find('hpg_enable=true') != -1) | (line.find('hpg_enable=false') != -1)) & (line.find('#') == -1)): 
         if (Huge_Pages == 1):
            s1.write("hpg_enable=true")
            s1.write("\n")
         else:
            s1.write("hpg_enable=false")
            s1.write("\n")
      #Enable or Disable NUMA
      elif (((line.find('numa_enable=true') != -1) | (line.find('numa_enable=false') != -1)) & (line.find('#') == -1)):
         if (NUMA == 1):
            s1.write("numa_enable=true")
            s1.write("\n")
         else:
            s1.write("numa_enable=false")
            s1.write("\n")
      #Enable or Disable ovs-dpdk
      elif (((line.find('ovs_dpdk_enable=true') != -1) | (line.find('ovs_dpdk_enable=false') != -1)) & (line.find('#') == -1)):
         if (OVS_DPDK == 1):
            s1.write("ovs_dpdk_enable=true")
            s1.write("\n")
         else:
            s1.write("ovs_dpdk_enable=false")
            s1.write("\n")
      #Enable or Disable SRIOV
      elif (((line.find('sriov_enable=true') != -1) | (line.find('sriov_enable=false') != -1)) & (line.find('#') == -1)):
         if (SRIOV == 1):
            s1.write("sriov_enable=true")
            s1.write("\n")
         else:
            s1.write("sriov_enable=false")
            s1.write("\n")
      #Enable or Disable dvr
      elif (((line.find('dvr_enable=true') != -1) | (line.find('dvr_enable=false') != -1)) & (line.find('#') == -1)):
         if (DVR == 1):
            s1.write("dvr_enable=true")
            s1.write("\n")
         else:
            s1.write("dvr_enable=false")
            s1.write("\n")
      #Enable or Disable Octavia
      elif (((line.find('octavia_enable=true') != -1) | (line.find('octavia_enable=false') != -1)) & (line.find('#') == -1)):
         if (Octavia == 1):
            s1.write("octavia_enable=true")
            s1.write("\n")
         else:
            s1.write("octavia_enable=false")
            s1.write("\n")
      #Enable or Disable Tempest
      elif (((line.find('run_tempest=true') != -1) | (line.find('run_tempest=false') != -1)) & (line.find('#') == -1)):
         if (Tempest == 1):
            s1.write("run_tempest=true")
            s1.write("\n")
         else:
            s1.write("run_tempest=false")
            s1.write("\n")
      #Enable or Disable Sanity
      elif (((line.find('run_sanity=true') != -1) | (line.find('run_sanity=false') != -1)) & (line.find('#') == -1)):
         if (Sanity == 1):
            s1.write("run_sanity=true")
            s1.write("\n")
         else:
            s1.write("run_sanity=false")
            s1.write("\n")
      elif (((line.find('nic_env_file=ovs-dpdk_9_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=sriov_7_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=sriov_9_port/nic_enviornment.yaml') != -1) | (line.find('nic_env_file=ovs-dpdk_sriov_9_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=5_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=4_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=dvr_7_port/nic_environment.yaml') != -1) | (line.find('nic_env_file=ovs-dpdk_7_port/nic_environment.yaml') != -1)) & (line.find('#') == -1)):
         print("************************************************")
         print(" 1 ---------> NUMA and HugePages with nic ports")
         print(" 2 ---------> OVS-DPDK with nic ports")
         print(" 3 ---------> SR-IOV with nic ports")
         print(" 4 ---------> OVS-DPDK and SR-IOV with nic ports")
         print(" 5 ---------> DVR with nic ports")
         print("************************************************")
         Option = int(input("Option : "))
         if(Option == 1):
            if( NUMA == 1 | Huge_Pages == 1 ):
               print("*********************************************")
               print(" 1 --------> NUMA and Huge Pages with 4_port")
               print(" 2 --------> NUMA and Huge Pages with 5_port")
               Ports = bool(input("Ports Option : "))
               if(Ports == 1 ):
                  s1.write("nic_env_file=4_port/nic_environment.yaml")
                  s1.write("\n") 
               elif(Ports == 2 ):
                  s1.write("nic_env_file=5_port/nic_environment.yaml")
                  s1.write("\n")
            else:
               print("*********************************************")
               print("Can't make required changes because NUMA/Huge Pages are not Enabled")   
               print("*********************************************")
         if(Option == 2):
            if( OVS_DPDK == 1 ):
               print("*********************************************")
               print(" 1 --------> OVS-DPDK with 7 ports")       
               print(" 2 --------> OVS-DPDK with 9 ports")
               Ports = bool(input("Ports Option : "))
               if(Ports == 1 ):
                  s1.write("nic_env_file=ovs-dpdk_7_port/nic_environment.yaml")
                  s1.write("\n")
               elif(Ports == 2 ):
                  s1.write("nic_env_file=ovs-dpdk_9_port/nic_environment.yaml")
                  s1.write("\n")
            else:
               print("*********************************************")
               print("Can't make required changes because OVS-DPDK is not Enabled")
               print("*********************************************")
         if(Option == 3):
            if( SRIOV == 1 ):
               print("*********************************************")
               print(" 1 --------> SRIOV with 7 ports")
               print(" 2 --------> SRIOV with 9 ports")
               Ports = bool(input("Ports Option : "))
               if(Ports == 1 ):
                  s1.write("nic_env_file=sriov_7_port/nic_environment.yaml")
                  s1.write("\n")
               elif(Ports == 2 ): 
                  s1.write("nic_env_file=sriov_9_port/nic_environment.yaml")
                  s1.write("\n")
            else:
               print("*********************************************")
               print("Can't make required changes because SRIOV is not Enabled")
               print("*********************************************")
         if(Option == 4):
            if( SRIOV == 1 & OVS_DPDK == 1 ):
               s1.write("nic_env_file=ovs-dpdk_sriov_9_port/nic_environment.yaml")
               s1.write("\n")
            else:
               print("*********************************************")
               print("Can't make required changes because SRIOV/OVS-DPDK is not Enabled")
               print("*********************************************")

         if(Option == 5):
            if( DVR == 1 ):
               print("*********************************************")
               print(" 1 --------> DVR for Storage and Floating networks that share a single bond, 5 ports")
               print(" 2 --------> DVR with 7 ports")
               Ports = bool(input("Ports Option : "))
               if(Ports == 1 ):
                  s1.write("nic_env_file=5_port/nic_environment.yaml")
                  s1.write("\n")
               elif(Ports == 2 ): 
                  s1.write("nic_env_file=dvr_7_port/nic_environment.yaml")
                  s1.write("\n")
            else:
               print("*********************************************")
               print("Can't make required changes because DVR is not Enabled")
               print("*********************************************")

      # Chose NIC
      elif (((line.find('HostNicDriver=vfio-pci') != -1) | (line.find('HostNicDriver=mlx5_core') != -1) | (line.find('#HostNicDriver=vfio-pci') != -1) | (line.find('#HostNicDriver=mlx5_core') != -1)) & (line.find('#') == -1)):
         if (OVS_DPDK == 1):
            print("******************************************")
            print("***************   NICs  ******************")
            print("******** 0 ----------> Intell NIC   ******")
            print("******** 1 ----------> Mellanox NIC ******")
            print("******************************************")
            NIC = bool(input("NIC : "))
            if (NIC == 0):
               s1.write("HostNicDriver=vfio-pci")
               s1.write("\n")
            elif (NIC == 1):
               s1.write("HostNicDriver=mlx5_core")
               s1.write("\n")
         else:
            s1.write("#HostNicDriver=vfio-pci")
            s1.write("\n")
      else:
         s1.write(line) 
   #end of for loops
   s.close()
   s1.close()
   #Show Status of NFV Features
   print
   print("******************************************")
   print("*********** Edited Successfully **********")
   print("******************************************")
   print
   print("********************************************")
   print("*           NFV Features Status            *")
   print("********************************************")
   if (Huge_Pages == 1):
      print("*******  1-[Huge Pages]='Enabled'    *******")
   else:
      print("*******  1-[Huge Pages]='Disabled'   *******")
   if (NUMA == 1 ):
      print("*******  2-[NUMA]='Enabled'          *******")
   else:
      print("*******  2-[NUMA]='Disabled'         *******")
   if (OVS_DPDK == 1 ):
      print("*******  3-[OVS-DPDK]='Enabled'      *******")
   else: 
      print("*******  3-[OVS-DPDK]='Disabled'     *******")
   if (SRIOV == 1 ):
      print("*******  4-[SRIOV]='Enabled'         *******")
   else:
      print("*******  4-[SRIOV]='Disabled'        *******")
   if (DVR == 1 ):
      print("*******  5-[DVR]='Enabled'           *******")
   else:
      print("*******  5-[DVR]='Disabled'          *******")
   if (Octavia == 1 ):
      print("*******  6-[Octavia]='Enabled'       *******")
   else:
      print("*******  6-[Octavia]='Disabled'      *******")
   if (Tempest == 1 ):
      print("*******  7-[Tempest]='Enabled'       *******")
   else:
      print("*******  7-[Tempest]='Disabled'      *******")
   if (Tempest_smoke == 1):
      print("*******  8-[Tempest Smoke]='Enabled' *******")
   else:
      print("*******  8-[Tempest Smoke]='Disabled' *******")
   if (Sanity == 1 ):
      print("*******  9-[Sanity]='Enabled'        *******")
   else:
      print("*******  9-[Sanity]='disabled'       *******")
   print("******************************************")
   print("******************************************")
   return
script_parameters()
os.rename(sys.argv[1], 'temp.txt')
os.rename('sample1.txt', sys.argv[1])
os.remove('temp.txt')



