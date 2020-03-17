#--------------------------------Pre requisit steps to run tempest ------------------------------------
# tempest init mytempest
# cd mytempest
# openstack network list --------> get uuid of 'public' network
# discover-tempest-config --deployer-input ~/tempest-deployer-input.conf --debug --create --network-id <UUID of public network>
#-------------------------------- Then run this script ------------------------------------------------
#!/bin/bash
counter=0
test_execuation()
{
  counter=$(($counter + 1))
  echo "======================================= Test Case Number : $counter ==============================================="
  echo "*** $1 ***"
  echo "============================================================================================================="
  
  echo "==================================== Test Case Number : $counter ============================================" >> octavia_tempest.log
  echo "========== $1 ============" >> octavia_tempest.log
  echo "=============================================================================================================" >> octavia_tempest.log
  
  output=$(tempest run --regex "($1)")
  echo "$output"
  echo "$output" >> octavia_tempest.log
  echo "============================================================================================================="
  echo "=============================================================================================================" >> octavia_tempest.log
}

##############################
echo "================================ Octavia Tempest Log File =====================" > octavia_tempest.log
output=$(ostestr -l | grep barbican)
octavia_test_cases_list=$(echo "$output" | awk 'BEGIN { FS="[" } /4/ { print $1}')
echo "$octavia_test_cases_list" > octavia_test_cases_list.txt

filename="octavia_test_cases_list.txt"
while read -r line; do
  test_execuation $line
done < "$filename"

