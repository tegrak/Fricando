AUTOMAKE_OPTIONS = gnu
ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST = AUTHORS \
             COPYING \
             NEWS \
             autogen.sh  

MAINTAINERCLEANFILES=\
	$(top_srcdir)/configure \
	$(top_srcdir)/Makefile.in \
	$(top_srcdir)/aclocal.m4 \
	$(top_srcdir)/compile \
	$(top_srcdir)/depcomp \
	$(top_srcdir)/install-sh \
	$(top_srcdir)/ltmain.sh \
	$(top_srcdir)/missing \
	$(top_srcdir)/config.guess \
	$(top_srcdir)/config.sub \
	$(top_srcdir)/config.h.in \
	$(top_srcdir)/config.h.in~ \
	$(top_srcdir)/m4/ltsugar.m4 \
	$(top_srcdir)/m4/libtool.m4 \
	$(top_srcdir)/m4/ltversion.m4 \
	$(top_srcdir)/m4/lt~obsolete.m4 \
	$(top_srcdir)/m4/ltoptions.m4

SUBDIRS = src

doc_DATA = README

dist-hook:
	$(MKDIR_P) "$(distdir)/m4"

libtool: $(LIBTOOL_DEPS)
	$(SHELL) ./config.status --recheck

libs:

distclean-local:
	@rm -rf Makefile.in
	@rm -rf aclocal.m4
	@rm -rf autom4te.cache/
	@rm -rf compile
	@rm -rf config.guess
	@rm -rf config.h.in
	@rm -rf config.h.in~
	@rm -rf config.sub
	@rm -rf configure
	@rm -rf depcomp
	@rm -rf install-sh
	@rm -rf ltmain.sh
	@rm -rf missing
	@rm -rf m4/ltsugar.m4
	@rm -rf m4/libtool.m4
	@rm -rf m4/ltversion.m4
	@rm -rf m4/lt~obsolete.m4
	@rm -rf m4/ltoptions.m4

