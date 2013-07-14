#!/bin/bash

dtctool=$1
$1 -p 1024 -I dts -O dtb -o sample.dtb msm8960-cdp.dts
