#!/bin/bash

# remove all ebs vols that are not in-use

tmp_file=`mktemp`
region=us-west-1

ec2-describe-volumes --region $region | grep -B1 ^ATTACHMENT | grep -v ^ATTACHMENT | grep ^VOLUME | awk '{print $2}' | tr '\n' '|' | sed 's/|$//' > $tmp_file
for v in `ec2-describe-volumes --region $region | egrep -wv -f $tmp_file | awk '{print $2}'`;do ec2-delete-volume --region $region $v;done
rm $tmp_file
