#!/bin/bash

dtctool=$1
$1 -p 1024 -I dtb -O dts -o sample.dts sample.dtb
