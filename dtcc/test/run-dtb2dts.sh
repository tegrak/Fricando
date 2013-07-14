#!/bin/bash

dtctool=$1
$dtctool -p 1024 -I dtb -O dts -o sample.dts sample.dtb
