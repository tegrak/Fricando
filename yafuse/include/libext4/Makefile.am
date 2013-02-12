MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

headers = libext4.h \
          ext4.h \
          ext4_extents.h \
          ext4_jbd2.h \
          jbd2.h

if INSTALL_LIBRARY
libext4include_HEADERS = $(headers)
else
noinst_HEADERS = $(headers)
endif
