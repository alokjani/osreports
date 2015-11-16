#!/bin/bash
# Ensure `admin` present with _role_ `admin` in all tenants
# --

for t in `keystone tenant-list | grep True | awk '{print $2}'`; 
do 

    rolelst=`keystone user-role-list --user admin --tenant $t | awk '{print $4}'`

    echo $rolelst | tr '\n' ' ' | grep -q admin

    if [ "$?" -ne "0" ]; then
        keystone user-role-add --user admin --tenant $t --role admin
        echo "Adding admin to tenant $t"
    else
        echo "admin:admin:$t"
    fi
  
done
