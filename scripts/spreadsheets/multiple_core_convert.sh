#!/bin/bash

# You must supply the amount of cores
if [ $# -eq 0 ]
	then
	echo "No arguments supplied"
	echo "USAGE: ./multiple_core_convert.sh <CORES>"
	exit -1
fi

# Spawn the necessary processes
START=0
END=$(($1-1))
for i in $( eval echo {$START..$END} )
do
	echo "Spawning process $((i + 1))"
	nohup python3 convert.py $i $(($END+1)) &
done
