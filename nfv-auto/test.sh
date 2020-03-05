#! /bin/bash
counter=0
output=$(ostestr -l | grep octavia)
test_cases_list=$(echo "$output" | awk 'BEGIN { FS="[" } /4/ { print $1}')
echo "$test_cases_list" > test_cases_list.txt
##############################################################
filename="test_cases_list.txt"
while read -r line; do
    counter=$(($counter+1))
    echo $counter
    echo "$line"
done < "$filename"


