#!/bin/bash


FILENAME=$1

if [ ! -f $FILENAME ];
then
    echo "$FILENAME not found"
    exit 1
fi


awk '{print $1,$5,$6,$11,$13}' $FILENAME > ${FILENAME}.preprocessed

#filter // for /
sed -i .bak 's/\/\//\//g' ${FILENAME}.preprocessed

#filter replace id for #
sed -i .bak "s/\/[0-9]\{0,9\}\//\/#\//g" ${FILENAME}.preprocessed

#filter ip
sed -i .bak 's/[0-9]\{3\}\.[0-9]\{3\}\.[0-9]\{3\}\.[0-9]\{3\}/#/g' ${FILENAME}.preprocessed

#filter vm-uuid
#sed -i .bak 's/vm\-.*[^\/]/vm-UUID/g' ${FILENAME}.preprocessed