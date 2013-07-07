MAINTAINERCLEANFILES = $(srcdir)/Makefile.in

bin_PROGRAMS = dtcc

dtcc_LDADD = $(top_builddir)/libfdt/libfdt.la

if REALLYSTATIC
dtcc_LDFLAGS = $(AM_LDFLAGS) -all-static
endif

dtcc_CFLAGS = $(AM_CFLAGS) \
              -I$(top_srcdir)/src/libfdt \
              -I$(top_srcdir)/src

dtcc_SOURCES  = dtc.c \
                checks.c \
                data.c \
                dtc-parser.c \
                fdtdump.c \
                fdtget.c \
                fdtput.c \
                flattree.c \
                fstree.c \
                livetree.c \
                srcpos.c \
                treesource.c \
                util.c \
                dtc-lexer.lex.c_shipped \
                dtc-parser.tab.c_shipped

if RUN_LDCONFIG
install-exec-hook:
	$(LDCONFIG)
endif
