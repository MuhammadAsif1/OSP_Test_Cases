# NFV_window
NFV_window repo contains RHOSP Cloud features test cases automation scripts. Automation scripts are written in Python and Bash. Follow given instructions to execute scripts.  
# Features List
| Features	       | No. of Test Cases Automated | Automation Language |
|------------------|-----------------------------|---------------------|
| Barbican	       |   20	                      |     Bash            |
| Octavia	       |   17	                      |     Python          |
| DVR	             |   44	                      |     Python          |
| HugePages	       |   10                        |     Bash            |
| Manila	          |   26	                      |     Python          |
| MTU	             |   30	                      |     Python          |
| SRIOV	          |   22	                      |     Python          |
| NUMA	          |   11	                      |     Python          |
| OVS-DPDK         |	  48	                      |     Python          |
| OVS-DPDK-&-SRIOV |   12	                      |     Python          |
| SRIOV_OVS-offload|	  16                        |     Python          |




# Guide to Execute Scripts:

# Pre-Request to run Automated test cases:
- Create ssh key
  > $ openstack keypair create ssh-key > ssh-key.pem

  > $ chmod 400 ssh-key.pem

- Create image or execute sanity script which automatically create public network and “centos” image on Openstack.
Image name should be ‘centos’

  ‘or’

  > $ source <overcloud>
   
  > $ python pilot/deployment-validation/sanity_test.sh

- If require then create availability zones by using python script

  > $ python NFV_window/nfv-auto/availability-zone-creation.sh

- Clone repository
  > https://github.com/MuhammadAsif1/NFV_window.git

- ‘setup.json’ contained parameters(network name, server name, zones etc) and features .py file will get these parameters values.
  Change stamp’s json file (e.g R8_stamp_data.json) according to the required parameter values.


# Execute Test Cases:
- Setup environment  
- Install virtualenv using pip on director
  > $ pip install virtualenv
- Create a virtual environment
  > $ virtualenv  <env-name>
- Active your virtual environment
  > $ source <env-name>/bin/activate
- Install paramiko and sdk package
  > $ pip install openstacksdk==0.22.0
   
  > $ pip install paramiko==2.4.2
