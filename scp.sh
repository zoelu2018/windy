#!/bin/bash

#string = $1
#array = (${string//,/})

for var in ${@:2}
do
scp /FY4COMM/FY4A/NWP/JSON/NWP_GBAL_$1_UV_${var}mb.JSON shk401@121.36.13.81:/SHKDATA/NWP/JSON/ ;
scp -o StrictHostKeyChecking=no /FY4COMM/FY4A/NWP/JSON/NWP_GBAL_$1_UV_${var}mb.JSON fy4@119.3.254.166:/FY4COMM/FY4A/NWP/JSON/ ;
done 
