#!/bin/bash


FILENAME=$1

if [ ! -f $FILENAME ];
then
    echo "$FILENAME not found"
    exit 1
fi

awk '{print $7,$11,$12,$17,$19}' $FILENAME > ${FILENAME}.preprocessed
#awk '{print $1,$5,$6,$11,$13}' $FILENAME > ${FILENAME}.preprocessed

# regexp online tester: http://www.regexr.com/

#filter // for /
sed -i 's@//@/@g' ${FILENAME}.preprocessed

#filter ip
sed -i 's/[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}/#/g' ${FILENAME}.preprocessed

#filter replace id for #
#sed -i .bak "s/\/[0-9]\{1,9\}\//\/#\//g" ${FILENAME}.preprocessed
sed -i "s@/[0-9]\{1,9\}[/]@/#/@g" ${FILENAME}.preprocessed

#filter replace uris ending with id without slash for #
sed -i "s@/[0-9]\{1,9\}[ ]@/#/ @g" ${FILENAME}.preprocessed

#filter uuid
sed -i 's/[a-fA-F0-9]\{8\}-[a-fA-F0-9]\{4\}-4[a-fA-F0-9]\{3\}-[89aAbB][a-fA-F0-9]\{3\}-[a-fA-F0-9]\{12\}/UUID/g' ${FILENAME}.preprocessed

#removes line that starts with [
sed -i '/^\[/d' ${FILENAME}.preprocessed