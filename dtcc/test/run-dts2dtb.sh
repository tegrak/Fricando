#!/bin/bash

dtctool=$1
$dtctool -p 1024 -I dts -O dtb -o sample.dtb msm8960-cdp.dts
