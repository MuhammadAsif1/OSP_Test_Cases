#! /bin/bash
x=$(cat /etc/hosts | grep cntl0)
cntl0=$(echo "$x" | awk -F " " ' {print $1}')
x=$(cat /etc/hosts | grep cntl1)
cntl1=$(echo "$x" | awk -F " " ' {print $1}')
x=$(cat /etc/hosts | grep cntl2)
cntl2=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep nova0)
nova0=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep nova1)
nova1=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep nova2)
nova2=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep stor0)
stor0=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep stor1)
stor1=$(echo "$x" | awk -F " " ' {print $1}')             
x=$(cat /etc/hosts | grep stor2)
stor2=$(echo "$x" | awk -F " " ' {print $1}')             
####################
 echo "{
  \"cntl0\" : \"$cntl0\",
  \"cntl1\" : \"$cntl1\",
  \"cntl2\" : \"$cntl2\",
  \"cmpt0\" : \"$nova0\",
  \"cmpt1\" : \"$nova1\",
  \"cmpt2\" : \"$nova2\",
  \"strg0\" : \"$stor0\",
  \"strg1\" : \"$stor1\",
  \"strg2\" : \"$stor2\",
  \"username_of_nodes\" : \"heat-admin\",
  \"sah_node_ip\" : \"100.67.153.8\",
  \"director_node_ip\" : \"100.67.154.9\",
  \"sah_node_username\" : \"root\",
  \"sah_node_password\" : \"Dell0SS!\",
  \"csp_profile_ini_file_path\" : \"/root/R153_sriov.ini\"
}
" > hosts.json
