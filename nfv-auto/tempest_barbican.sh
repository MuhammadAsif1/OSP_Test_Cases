#!/bin/bash
counter=0
line=''
test_execuation()
{
  counter=$(($counter + 1))
  echo "======================================= Test Case Number : $counter ==============================================="
  echo "*** $1 ***"
  echo "============================================================================================================="
  
  echo "==================================== Test Case Number : $counter ============================================" >> barbican_tempest.log
  echo "========== $1 ============" >> barbican_tempest.log
  echo "=============================================================================================================" >> barbican_tempest.log
  
  output=$(tempest run --regex "($1)")
  echo "$output"
  echo "$output" >> barbican_tempest.log
  echo "============================================================================================================="
  echo "=============================================================================================================" >> barbican_tempest.log
}

##############################
echo "================================ Barbican Tempest Log File =====================" > barbican_tempest.log
output=$(ostestr -l | grep barbican)
barbican_test_cases_list=$(echo "$output" | awk 'BEGIN { FS="[" } /4/ { print $1}')
echo "$barbican_test_cases_list" > barbican_test_cases_list.txt

filename="barbican_test_cases_list.txt"
while read -r line; do
  test_execuation $line
done < "$filename"

