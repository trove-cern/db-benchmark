#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Please supply either read_write, read_only, write_only or prepare/cleanup as the first argument"
    exit 1
fi


user="trove"
password="********"
db_name="sbtest1"
driver="mysql"

static_options="--mysql-user=${user} --mysql-password=${password} --mysql-db=${db_name} --db-driver=${driver}"

run_time=60


if [ $1 = "prepare" ]; then
    if [ $# -lt 2 ]; then
        echo "Please give the number of rows to create in the table as the second argument"
        exit 1
    fi
    static_prepare="--table-size=${2}"
    
    for host in "std" "io1" "root"; do
        echo "Preparing database on ${host}"
        duration="$(time ( sysbench --mysql-host=th-benchmark-db-${host}.cern.ch ${static_prepare} ${static_options} oltp_read_write prepare ) 2>&1 )"
        echo "$duration"
        echo "###########################################################"
        echo ""
    done
    echo "Preparing database on dbod"
    duration="$(time ( sysbench --mysql-host=dbod-ostest01 --mysql-port=5502 ${static_prepare} ${static_options} oltp_read_write prepare ) 2>&1 1>/dev/null )"
    echo "$duration"
    echo ""
    
    echo "${2}" > .tablesize
    exit 0
fi

if [ $1 = "cleanup" ]; then
    for host in "std" "io1" "root"; do
        echo "Cleaning ${host}"
        sysbench --mysql-host=th-benchmark-db-${host}.cern.ch ${static_options} oltp_read_write cleanup
        echo "######################################################"
    done
    echo "Cleaning dbod"
    sysbench --mysql-host=dbod-ostest01 --mysql-port=5502 ${static_options} oltp_read_write cleanup
    exit 0
fi
    



current_time=`date +%s`

if [ -d latest ]; then
    timestamp=`cat latest/.timestamp`
    mv "latest" "${timestamp}"
fi


mkdir "latest"
echo "${current_time}" > "latest/.timestamp"
echo "${1}" > "latest/.benchmark"
echo "${run_time}" > "latest/.runtime"
echo `cat .tablesize` > "latest/.tablesize"


for host in "std" "io1" "root"; do
        
    for threads in 1 2 4 8; do
        echo ""
        echo "####################################################################"
        echo "Running ${1} test for ${threads} threads on th-benchmark-db-${host}.cern.ch"
        echo "####################################################################"
        echo ""
        sysbench --time=${run_time} --threads=${threads} --mysql-host=th-benchmark-db-${host}.cern.ch ${static_options} oltp_${1} run | tee "latest/sb-${host}-${threads}"
    done
    
done


for threads in 1 2 4 8; do
    echo ""
    echo "####################################################################"
    echo "Running ${1} test for ${threads} threads on dbod-ostest01"
    echo "####################################################################"
    echo ""
    sysbench --time=${run_time} --threads=${threads} --mysql-host=dbod-ostest01 --mysql-port=5502 ${static_options} oltp_${1} run | tee "latest/sb-dbod-${threads}"
done
