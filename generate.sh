#!/bin/sh

if [ "X$1" == "X" ]; then
	echo $0 "<name> <rows> <number of processes> <delimiter>"
	exit -2
fi

FILENAME=$1
ROWS=$2
if [ "X$ROWS" == "X" ]; then
	ROWS=1000000
fi
N=$3
if [ "X$N" ==  "X" ]; then
	N=1
fi
DELIM=$4
if [ "X$DELIM" ==  "X" ]; then
	DELIM='|'
fi

rm -f ${FILENAME}.csv
for i in $(eval echo "{1..$N}")
do
	python csvgen.py -i $ROWS -d $DELIM -o ${FILENAME}.csv.${i}  ${FILENAME}.in &

done

wait
for i in $(eval echo "{1..$N}")
do
	cat ${FILENAME}.csv.${i} >> ${FILENAME}.csv
	rm -f ${FILENAME}.csv.${i}
done

