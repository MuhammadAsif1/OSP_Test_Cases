#!/bin/bash
counter=0
line=''

reboot_nodes()
{   echo "================ REBOOTING ALL NODES ========================"
    echo "================ REBOOTING ALL NODES ========================">> node_clean.log
  output=$(nova reboot $1)
  echo "$output"
  echo "$output" >> node_clean.log
  echo "============================================================================================================="
  echo "=============================================================================================================" >> node_clean.log
}

echo "================================ Node Reboot Log File =====================" > node_clean.log
output=$(nova list)
stack_node_ids=$(echo "$output" | awk -F "|" '/-/ { print $2}')
echo $output
echo $stack_node_ids

echo "$stack_node_ids" > stack_node_id_list.txt
#=============Rebooting Stack nodes==========
echo "=============Rebooting Stack nodes=========="

filename="stack_node_id_list.txt"
while read -r line; do
#    reboot_nodes $line
    if [ $line ]
    then
        echo "Stack Node id is $line"
        reboot_nodes $line
    else
        echo "No line to Print"
    fi
done < "$filename"

nova list
