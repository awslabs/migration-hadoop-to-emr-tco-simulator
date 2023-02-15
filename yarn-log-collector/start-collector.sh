#!/bin/sh

#HTTP Secure Mode : [1] HTTPS with Kerberos Case [2] HTTPS Case [3] HTTP Case 
#YARN Resource Manager URL form:
#[HTTPS] yarn-resoure-manager-ip-adress:8090
#[HTTP] yarn-resoure-manager-ip-adress:8088

while getopts m:u: flag
do
  case "${flag}" in
    m) mode=${OPTARG};;
    u) url=${OPTARG};;
  esac
done

if [[ -z "${url}" ]]; then
  echo "### Get emr list-clusters --active."

  list=$(aws emr list-clusters --active | jq -r ".Clusters[].Id")
  for id in ${list} ; do
    dns=$(aws emr describe-cluster --cluster-id ${id} |
      jq -r ".Cluster.MasterPublicDnsName")
    dns=$(echo ${dns} |
      sed -r "s/ip-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)\.[[:alnum:]-]*\.compute\.internal/\1.\2.\3.\4/g")

    name=$(aws emr describe-cluster --cluster-id ${id} |
      jq -r ".Cluster.Name")
    echo ${dns} ${name}

    url="${url} ${dns}"
  done
fi

for i in ${url} ; do
  output=customer-yarn-logs-json-${i}-$(date +"%Y-%m-%d-%T").json
  cluster_api=/ws/v1/cluster/apps

  echo "### Start yarn logs collecting from curl."
  echo "### HTTP Secure-Mode: ${mode}"
  echo "### YARN-RM URL: ${i}"

  if [ $mode -eq 1 ]
  then
    echo "### HTTPS with Kerberos Case"
    target=https://${i}:8090${cluster_api}
    curl -k --negotiate -u: -X GET {target} > ${output}
  elif [ $mode -eq 2 ]
  then
    echo "### HTTPS Case"
    target=https://${i}:8090${cluster_api}
    curl -k -u: -X GET ${target} > ${output}
  elif [ $mode -eq 3 ]
  then
    echo "### HTTP Case"
    target=http://${i}:8088${cluster_api}
    curl -X GET ${target} > ${output}
  fi

  echo "### Yarn Cluter API target: ${target}"
done

echo "### Collecting yarn logs completed."
