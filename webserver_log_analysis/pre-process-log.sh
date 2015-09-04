#!/bin/bash


FILENAME=$1

if [ ! -f $FILENAME ];
then
    echo "$FILENAME not found"
    exit 1
fi

awk '{print $7,$11,$12,$17,$19}' $FILENAME > ${FILENAME}.preprocessed
#awk '{print $1,$5,$6,$11,$13}' $FILENAME > ${FILENAME}.preprocessed

#filter // for /
sed -i .bak 's/\/\//\//g' ${FILENAME}.preprocessed

#filter replace id for #
sed -i .bak "s/\/[0-9]\{0,9\}\//\/#\//g" ${FILENAME}.preprocessed

#filter ip
sed -i .bak 's/[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}/#/g' ${FILENAME}.preprocessed

#filter uuid
sed -i .bak 's/[a-fA-F0-9]\{8\}-[a-fA-F0-9]\{4\}-4[a-fA-F0-9]\{3\}-[89aAbB][a-fA-F0-9]\{3\}-[a-fA-F0-9]\{12\}/UUID/g' ${FILENAME}.preprocessed

#removes line that starts with [
sed -f .bak sed '/^\[/d' ${FILENAME}.preprocessed