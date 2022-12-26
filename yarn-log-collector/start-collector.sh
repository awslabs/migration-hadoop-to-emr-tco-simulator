#!/bin/sh

#HTTP Secure Mode : [1] HTTPS with Kerberos Case [2] HTTPS Case [3] HTTP Case 
#YARN Resource Manager URL form:
#[HTTPS] https://yarn-resoure-manager-ip-adress:8090
#[HTTP] http://yarn-resoure-manager-ip-adress:8088 

while getopts m:u: flag
do
    case "${flag}" in
        m) mode=${OPTARG};;
        u) url=${OPTARG};;
    esac
done

output=customer-yarn-logs-json-$(date +"%Y-%m-%d-%T").json
cluster_api="/ws/v1/cluster/apps"
target="${url}${cluster_api}"

echo "Start yarn logs collecting from curl."
echo "HTTP Secure-Mode: $mode"
echo "YARN-RM URL: $url"
echo "Yarn Cluter API target: $target"

if [ $mode -eq 1 ]
then
  echo "HTTPS with Kerberos Case"
  curl -k --negotiate -u: -X GET $target > ${output}
elif [ $mode -eq 2 ]
then
  echo "HTTPS Case"
  curl -k -u: -X GET $target > ${output}
elif [ $mode -eq 3 ]
then
  echo "HTTP Case"
  curl -X GET $target > ${output}
fi

echo "Collecting yarn logs completed."
