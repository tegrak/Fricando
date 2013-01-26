#!/bin/bash

export CFLAGS="$CFLAGS -I/opt/readline-6.2/include -I/opt/ncurses-5.9/include"
export LDFLAGS="$LDFLAGS -L/opt/readline-6.2/lib -L/opt/ncurses-5.9/lib"
export LIBS="$LIBS -lreadline -lncurses"

./configure
make && make install
./out/bin/yafuse -v ext4.img

