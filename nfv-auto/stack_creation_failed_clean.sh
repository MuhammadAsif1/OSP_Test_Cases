#!/bin/bash
counter=0
line=''

setting_Maintenance()
{   echo "================ Setting Node Maintenanace MOde to True ========================"
    echo "================ Setting Node Maintenanace MOde to True ========================">> node_clean.log
  output=$(ironic node-set-maintenance $1 true)
  echo "$output"
  echo "$output" >> node_clean.log
  echo "============================================================================================================="
  echo "=============================================================================================================" >> node_clean.log
}

deleting_node()
{   echo "================ Deleting Nodes ========================"
    echo "================ Deleting Nodes ========================">> node_clean.log
  output=$(ironic node-delete $1)
  echo "$output"
  echo "$output" >> node_clean.log
  echo "============================================================================================================="
  echo "=============================================================================================================" >> node_clean.log
}

echo "================================ Node Clean Log File =====================" > node_clean.log
output=$(ironic node-list)
echo $output
node_uuids=$(echo "$output" | awk -F "|" '/-/ {print $2}')
echo "$node_uuids" > node_uuid_list.txt
echo $node_uuids

#power_status=$(echo "$output" | awk -F "|" '/-/ { print $1}')
#echo "$node_uuids" > node_uuid_list.txt
#echo "$power_status" > node_power_status.txt
##=============maintenanace and deletion==========
filename="node_uuid_list.txt"
while read -r line; do
    if [ $line ]
    then
        setting_Maintenance $line
        echo "Node uuid is $line"
    else
        echo "There is No UUID Present ..............."
    fi
done < "$filename"

ironic node-list

filename="node_uuid_list.txt"
while read -r line; do
    if [ $line ]
    then
        deleting_node $line
        echo "Node uuid is $line"
    else
        echo "There is No UUID Present ..............."
    fi

done < "$filename"

ironic node-list

cd
rm -rf instackenv.json

