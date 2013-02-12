MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

SUBDIRS = libio \
          libext4 \
          libfat32

headers = debug.h \
          types.h

if INSTALL_LIBRARY
include_HEADERS = $(headers)
else
noinst_HEADERS = $(headers)
endif
