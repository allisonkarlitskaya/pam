%define WITH_SELINUX 1

%define _sbindir /sbin
%define _sysconfdir /etc

%define pwdb_version 0.62
%define db_version 4.3.27
%define db_conflicting_version 4.4.0
%define pam_redhat_release 5

Summary: A security tool which provides authentication for applications.
Name: pam
Version: 0.78
Release: 9
License: GPL or BSD
Group: System Environment/Base
Source0: ftp.us.kernel.org:/pub/linux/libs/pam/pre/library/Linux-PAM-%{version}.tar.bz2
Source1: ftp.us.kernel.org:/pub/linux/libs/pam/pre/library/Linux-PAM-%{version}.tar.bz2.sign
Source2: pam-redhat-%{version}-%{pam_redhat_release}.tar.bz2
Source3: pwdb-%{pwdb_version}.tar.gz
Source4: db-%{db_version}.tar.gz
Source5: other.pamd
Source6: system-auth.pamd
Source8: dlopen.sh
Patch4: pam-0.75-prompt.patch
Patch10: pam-0.77-lastlog-utmp.patch
Patch21: pam-0.78-unix-hpux-aging.patch
Patch28: pam-0.75-sgml2latex.patch
Patch29: pam-0.78-multicrack.patch
Patch34: pam-0.77-dbpam.patch
Patch60: pam-0.78-selinux.patch
Patch61: pam-pwdbselinux.patch
Patch84: pam-0.77-unix-passwd-parse.patch
Patch90: pam-0.78-loginuid.patch
Patch91: pam-0.78-console-wrong-log.patch
Patch92: pam-0.78-console-alsa-init.patch
Patch93: pam-0.78-console-perms-dri.patch

BuildRoot: %{_tmppath}/%{name}-root
Requires: cracklib, cracklib-dicts, glib2, initscripts >= 3.94
Obsoletes: pamconfig
Prereq: grep, mktemp, sed, coreutils, /sbin/ldconfig
BuildPrereq: autoconf, bison, flex, glib2-devel, sed, cracklib, cracklib-dicts
BuildPrereq: perl, pkgconfig
%if %{WITH_SELINUX}
BuildPrereq: libselinux-devel >= 1.17.1
Requires: libselinux >= 1.17.1
%endif
URL: http://www.us.kernel.org/pub/linux/libs/pam/index.html

# We internalize libdb to get a non-threaded copy, but we should at least try
# to coexist with the system's copy of libdb, which will be used to make the
# files for use by pam_userdb (either by db_load or Perl's DB_File module).
Conflicts: db4 >= %{db_conflicting_version}

%description
PAM (Pluggable Authentication Modules) is a system security tool that
allows system administrators to set authentication policy without
having to recompile programs that handle authentication.

%package devel
Group: Development/Libraries
Summary: Files needed for developing PAM-aware applications and modules for PAM.
Requires: pam = %{version}-%{release}

%description devel
PAM (Pluggable Authentication Modules) is a system security tool that
allows system administrators to set authentication policy without
having to recompile programs that handle authentication. This package
contains header files and static libraries used for building both
PAM-aware applications and modules for use with PAM.

%prep
%setup -q -n Linux-PAM-%{version} -a 2 -a 3 -a 4
cp $RPM_SOURCE_DIR/other.pamd .
cp $RPM_SOURCE_DIR/system-auth.pamd .

%patch4  -p1 -b .prompt
%patch10 -p1 -b .lastlog-utmp
%patch21 -p1 -b .unix-hpux-aging
%patch28 -p1 -b .doc
%patch29 -p1 -b .multicrack
%patch34 -p1 -b .dbpam
%if %{WITH_SELINUX}
%patch60 -p1 -b .selinux
%patch61 -p1 -b .pwdbselinux 
%endif
%patch84 -p1 -b .passwd-parse
%patch90 -p1 -b .loginuid
%patch91 -p1 -b .wrong-log
%patch92 -p1 -b .alsa-init
%patch93 -p1 -b .dri

for readme in modules/pam_*/README ; do
	cp -f ${readme} doc/txts/README.`dirname ${readme} | sed -e 's|^modules/||'`
done
autoconf

%build
CFLAGS="-fPIC $RPM_OPT_FLAGS" ; export CFLAGS

topdir=`pwd`/pam-instroot
test -d ${topdir}         || mkdir ${topdir}
test -d ${topdir}/include || mkdir ${topdir}/include
test -d ${topdir}/%{_lib} || mkdir ${topdir}/%{_lib}

pushd db-%{db_version}/build_unix
echo db_cv_mutex=UNIX/fcntl > config.cache
../dist/configure -C \
	--disable-compat185 \
	--disable-cxx \
	--disable-diagnostic \
	--disable-dump185 \
	--disable-java \
	--disable-rpc \
	--disable-tcl \
	--disable-shared \
	--with-pic \
	--with-uniquename=_pam \
	--with-mutex="UNIX/fcntl" \
	--prefix=${topdir} \
	--includedir=${topdir}/include \
	--libdir=${topdir}/%{_lib}
make
make install
popd

pushd pwdb-%{pwdb_version}
make 
make install INCLUDED=${topdir}/include/pwdb LIBDIR=${topdir}/%{_lib} LDCONFIG=:
rm ${topdir}/%{_lib}/*.so*
popd

CPPFLAGS=-I${topdir}/include ; export CPPFLAGS
export LIBNAME="%{_lib}"
LDFLAGS=-L${topdir}/%{_lib} ; export LDFLAGS
%configure \
	--libdir=/%{_lib} \
	--enable-static-libpam \
	--enable-fakeroot=$RPM_BUILD_ROOT \
	--enable-isadir=../../%{_lib}/security
make

%install
rm -rf $RPM_BUILD_ROOT
# Install the binaries, libraries, and modules.
make install FAKEROOT=$RPM_BUILD_ROOT LDCONFIG=:

# Install default configuration files.
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -m 644 other.pamd $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/other
install -m 644 system-auth.pamd $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/system-auth
install -m 600 /dev/null $RPM_BUILD_ROOT%{_sysconfdir}/security/opasswd

# Forcibly strip binaries.
strip $RPM_BUILD_ROOT%{_sbindir}/* ||:

# Remove docs for modules we exclude from the files manifest.
#rm doc/*/*pam_timestamp*

# Install man pages.
install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man{3,5,8}
install -m 644 doc/man/*.3 $RPM_BUILD_ROOT%{_mandir}/man3/
install -m 644 doc/man/*.8 $RPM_BUILD_ROOT%{_mandir}/man8/

# Move static libraries and make new .so links -- this depends on the value
# of _libdir not changing, and *not* being /usr/lib.
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}
for lib in libpam libpamc libpam_misc ; do
ln -sf ../../%{_lib}/${lib}.so.%{version} $RPM_BUILD_ROOT%{_libdir}/${lib}.so
ln -sf ${lib}.so.%{version} $RPM_BUILD_ROOT/%{_lib}/${lib}.so
mv $RPM_BUILD_ROOT/%{_lib}/${lib}.a $RPM_BUILD_ROOT%{_libdir}/
done

# Make sure every module subdirectory gave us a module.  Yes, this is hackish.
for dir in modules/pam_* ; do
if [ -d ${dir} ] ; then
	if ! ls -1 $RPM_BUILD_ROOT/%{_lib}/security/`basename ${dir}`*.so ; then
		echo ERROR `basename ${dir}` did not build a module.
		exit 1
	fi
fi
done

# Install the pwdb configuration file.
install -m644 pwdb-%{pwdb_version}/conf/pwdb.conf $RPM_BUILD_ROOT%{_sysconfdir}/

# Remove unwanted files from the buildroot.
rm $RPM_BUILD_ROOT/%{_lib}/security/pam_radius.so
rm -f doc/txts/README.pam_radius

# Duplicate doc file sets.
rm -fr $RPM_BUILD_ROOT/usr/doc/Linux-PAM $RPM_BUILD_ROOT/usr/share/doc/pam

# Create /lib/security in case it isn't the same as /%{_lib}/security.
install -m755 -d $RPM_BUILD_ROOT/lib/security

# Check for module problems.  Specifically, check that every module we just
# installed can actually be loaded by a minimal PAM-aware application.
for module in $RPM_BUILD_ROOT/%{_lib}/security/pam*.so ; do
	if ! $RPM_SOURCE_DIR/dlopen.sh -lpam -ldl -L$RPM_BUILD_ROOT/%{_lib} ${module} ; then
		echo ERROR module: ${module} cannot be loaded.
		exit 1
	fi
# And for good measure, make sure that none of the modules pull in threading
# libraries, which if loaded in a non-threaded application, can cause Very
# Bad Things to happen.
	if env LD_PRELOAD=$RPM_BUILD_ROOT/%{_lib}/libpam.so ldd -r ${module} | fgrep -q libpthread ; then
		echo ERROR module: ${module} pulls threading libraries.
		exit 1
	fi
done

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# Figure whether or not we're using shadow/md5 passwords if we're upgrading.
if [ -f %{_sysconfdir}/pam.d/other ] ; then
	USEMD5=
	if [ -f /etc/sysconfig/authconfig ] ; then
		. /etc/sysconfig/authconfig
	fi
	if [ -z "$USEMD5" ] ; then
		if [ -f /etc/shadow ] ; then
			passwdfiles="/etc/passwd /etc/shadow"
		else
			passwdfiles="/etc/passwd"
		fi
		if cut -f2 -d: $passwdfiles | grep -q '^\$1\$' ; then
			echo USEMD5=yes >> /etc/sysconfig/authconfig
			USEMD5=yes
		else
			echo USEMD5=no  >> /etc/sysconfig/authconfig
			USEMD5=no
		fi
	fi
fi
exit 0

%post
/sbin/ldconfig
if [ ! -f /etc/shadow ] ; then
	tmp=`mktemp /etc/pam.d/pam-post.XXXXXX`
	if [ -n "$tmp" ] ; then
		sed 's| shadow||g' /etc/pam.d/system-auth > $tmp && \
		cat $tmp > /etc/pam.d/system-auth
		rm -f $tmp
	fi
fi
if [ -f /etc/sysconfig/authconfig ] ; then
	. /etc/sysconfig/authconfig
fi
if [ "$USEMD5" = "no" ] ; then
	tmp=`mktemp /etc/pam.d/pam-post.XXXXXX`
	if [ -n "$tmp" ] ; then
		sed 's| md5||g' /etc/pam.d/system-auth > $tmp && \
		cat $tmp > /etc/pam.d/system-auth
		rm -f $tmp
	fi
fi

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%config /etc/pwdb.conf
%dir /etc/pam.d
%config(noreplace) /etc/pam.d/other
%config(noreplace) /etc/pam.d/system-auth
%doc Copyright
%doc doc/html doc/ps doc/txts doc/pdf
%doc doc/specs/rfc86.0.txt
/%{_lib}/libpam.so.*
/%{_lib}/libpamc.so.*
/%{_lib}/libpam_misc.so.*
%{_sbindir}/pam_console_apply
%{_sbindir}/pam_tally
%{_sbindir}/pam_timestamp_check
%{_sbindir}/pwdb_chkpwd
%{_sbindir}/unix_chkpwd
%if %{_lib} != lib
%dir /lib/security
%endif
%dir /%{_lib}/security
/%{_lib}/security/pam_access.so
/%{_lib}/security/pam_chroot.so
/%{_lib}/security/pam_console.so
/%{_lib}/security/pam_cracklib.so
/%{_lib}/security/pam_debug.so
/%{_lib}/security/pam_deny.so
/%{_lib}/security/pam_env.so
/%{_lib}/security/pam_filter.so
/%{_lib}/security/pam_ftp.so
/%{_lib}/security/pam_group.so
/%{_lib}/security/pam_issue.so
/%{_lib}/security/pam_lastlog.so
/%{_lib}/security/pam_limits.so
/%{_lib}/security/pam_listfile.so
/%{_lib}/security/pam_localuser.so
/%{_lib}/security/pam_loginuid.so
/%{_lib}/security/pam_mail.so
/%{_lib}/security/pam_mkhomedir.so
/%{_lib}/security/pam_motd.so
/%{_lib}/security/pam_nologin.so
/%{_lib}/security/pam_permit.so
/%{_lib}/security/pam_postgresok.so
/%{_lib}/security/pam_pwdb.so
/%{_lib}/security/pam_rhosts_auth.so
/%{_lib}/security/pam_rootok.so
/%{_lib}/security/pam_rps.so
%if %{WITH_SELINUX}
/%{_lib}/security/pam_selinux.so
%endif
/%{_lib}/security/pam_securetty.so
/%{_lib}/security/pam_shells.so
/%{_lib}/security/pam_stack.so
/%{_lib}/security/pam_stress.so
/%{_lib}/security/pam_succeed_if.so
/%{_lib}/security/pam_tally.so
/%{_lib}/security/pam_time.so
/%{_lib}/security/pam_timestamp.so
/%{_lib}/security/pam_unix.so
/%{_lib}/security/pam_unix_acct.so
/%{_lib}/security/pam_unix_auth.so
/%{_lib}/security/pam_unix_passwd.so
/%{_lib}/security/pam_unix_session.so
/%{_lib}/security/pam_userdb.so
/%{_lib}/security/pam_warn.so
/%{_lib}/security/pam_wheel.so
/%{_lib}/security/pam_xauth.so
/%{_lib}/security/pam_filter
%dir %{_sysconfdir}/security
%config(noreplace) %{_sysconfdir}/security/access.conf
%config(noreplace) %{_sysconfdir}/security/chroot.conf
%config(noreplace) %{_sysconfdir}/security/console.perms
%config(noreplace) %{_sysconfdir}/security/console.handlers
%config(noreplace) %{_sysconfdir}/security/group.conf
%config(noreplace) %{_sysconfdir}/security/limits.conf
%config(noreplace) %{_sysconfdir}/security/pam_env.conf
%config(noreplace) %{_sysconfdir}/security/time.conf
%config(noreplace) %{_sysconfdir}/security/opasswd
%dir %{_sysconfdir}/security/console.apps
%dir /var/run/console
%{_mandir}/man5/*
%{_mandir}/man8/*

%files devel
%defattr(-,root,root)
%{_includedir}/security/
%{_mandir}/man3/*
%{_libdir}/libpam.a
%{_libdir}/libpam.so
%{_libdir}/libpamc.a
%{_libdir}/libpamc.so
%{_libdir}/libpam_misc.a
%{_libdir}/libpam_misc.so

%changelog
* Wed Mar 23 2005 Tomas Mraz <tmraz@redhat.com> 0.78-9
- fix wrong logging in pam_console handlers
- add executing ainit handler for alsa sound dmix
- #147879, #112777 - change permissions for dri devices

* Fri Mar 18 2005 Tomas Mraz <tmraz@redhat.com> 0.78-8
- remove ownership and permissions handling from pam_console call
  pam_console_apply as a handler instead

* Mon Mar 14 2005 Tomas Mraz <tmraz@redhat.com> 0.78-7
- add pam_loginuid module for setting the the login uid for auditing purposes
  (by Steve Grubb)

* Thu Mar 10 2005 Tomas Mraz <tmraz@redhat.com> 0.78-6
- add functionality for running handler executables from pam_console
  when console lock was obtained/lost
- removed patches merged to pam-redhat

* Tue Mar  1 2005 Tomas Mraz <tmraz@redhat.com> 0.78-5
- echo why tests failed when rebuilding
- fixed some warnings and errors in pam_console for gcc4 build
- improved parsing pam_console config file

* Mon Feb 21 2005 Tomas Mraz <tmraz@redhat.com>
- don't log garbage in pam_console_apply (#147879)

* Tue Jan 18 2005 Tomas Mraz <tmraz@redhat.com>
- don't require exact db4 version only conflict with incompatible one

* Wed Jan 12 2005 Tomas Mraz <tmraz@redhat.com> 0.78-4
- updated pam-redhat from elvis CVS
- removed obsolete patches

* Mon Jan  3 2005 Jeff Johnson <jbj@redhat.com> 0.78-3
- depend on db-4.3.27, not db-4.3.21.

* Thu Nov 25 2004 Tomas Mraz <tmraz@redhat.com> 0.78-2
- add argument to pam_console_apply to restrict its work to specified files

* Tue Nov 23 2004 Tomas Mraz <tmraz@redhat.com> 0.78-1
- update to Linux-PAM-0.78
- #140451 parse passwd entries correctly and test for failure
- #137802 allow using pam_console for authentication

* Fri Nov 12 2004 Jeff Johnson <jbj@jbj.org> 0.77-67
- rebuild against db-4.3.21.

* Thu Nov 11 2004 Tomas Mraz <tmraz@redhat.com> 0.77-66
- #77646 log failures when renaming the files when changing password
- Log failure on missing /etc/security/opasswd when remember option is present

* Wed Nov 10 2004 Tomas Mraz <tmraz@redhat.com>
- #87628 pam_timestamp remembers authorization after logout
- #116956 fixed memory leaks in pam_stack

* Wed Oct 20 2004 Tomas Mraz <tmraz@redhat.com> 0.77-65
- #74062 modify the pwd-lock patch to remove NIS passwd changing deadlock

* Wed Oct 20 2004 Tomas Mraz <tmraz@redhat.com> 0.77-64
- #134941 pam_console should check X11 socket only on login

* Tue Oct 19 2004 Tomas Mraz <tmraz@redhat.com> 0.77-63
- Fix checking of group %group syntax in pam_limits
- Drop fencepost patch as it was already fixed 
  by upstream change from 0.75 to 0.77
- Fix brokenshadow patch

* Mon Oct 11 2004 Tomas Mraz <tmraz@redhat.com> 0.77-62
- Added bluetooth, raw1394 and flash to console.perms
- pam_console manpage fix 

* Mon Oct 11 2004 Tomas Mraz <tmraz@redhat.com> 0.77-61
- #129328 pam_env shouldn't abort on missing /etc/environment
- #126985 pam_stack should always copy the conversation function 
- #127524 add /etc/security/opasswd to files

* Tue Sep 28 2004 Phil Knirsch <pknirsch@redhat.com> 0.77-60
- Drop last patch again, fixed now correctly elsewhere

* Thu Sep 23 2004 Phil Knirsch <pknirsch@redhat.com> 0.77-59
- Fixed bug in pam_env where wrong initializer was used

* Fri Sep 17 2004 Dan Walsh <dwalsh@redhat.com> 0.77-58
- rebuild selinux patch using checkPasswdAccess

* Mon Sep 13 2004 Jindrich Novy <jnovy@redhat.com>
- rebuilt

* Mon Sep 13 2004 Tomas Mraz <tmraz@redhat.com> 0.77-56
- #75454 fixed locking when changing password
- #127054 
- #125653 removed unnecessary getgrouplist call
- #124979 added quiet option to pam_succeed_if

* Mon Aug 30 2004 Warren Togami <wtogami@redhat.com> 0.77-55
- #126024 /dev/pmu console perms

* Wed Aug 4 2004 Dan Walsh <dwalsh@redhat.com> 0.77-54
- Move pam_console.lock to /var/run/console/

* Thu Jul 29 2004 Dan Walsh <dwalsh@redhat.com> 0.77-53
- Close fd[1] before pam_modutilread so that unix_verify will complete 

* Tue Jul 27 2004 Alan Cox <alan@redhat.com> 0.77-52
- First chunk of Steve Grubb's resource leak and other fixes

* Tue Jul 27 2004 Alan Cox <alan@redhat.com> 0.77-51
- Fixed build testing of modules
- Fixed dependancies

* Tue Jul 20 2004 Dan Walsh <dwalsh@redhat.com> 0.77-50
- Change unix_chkpwd to return pam error codes

* Sat Jul 10 2004 Alan Cox <alan@redhat.com>
- Fixed the pam glib2 dependancy issue

* Mon Jun 21 2004 Alan Cox <alan@redhat.com>
- Fixed the pam_limits fencepost error (#79989) since nobody seems to
  be doing it

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun 9 2004 Dan Walsh <dwalsh@redhat.com> 0.77-45
- Add requires libselinux > 1.8

* Thu Jun 3 2004 Dan Walsh <dwalsh@redhat.com> 0.77-44
- Add MLS Support to selinux patch

* Wed Jun 2 2004 Dan Walsh <dwalsh@redhat.com> 0.77-43
- Modify pam_selinux to use open and close param

* Fri May 28 2004 Dan Walsh <dwalsh@redhat.com> 0.77-42
- Split pam module into two parts open and close

* Tue May 18 2004 Phil Knirsch <pknirsch@redhat.com> 0.77-41
- Fixed 64bit segfault in pam_succeed_if module.

* Thu Apr 14 2004 Dan Walsh <dwalsh@redhat.com> 0.77-40
- Apply changes from audit.

* Tue Apr 12 2004 Dan Walsh <dwalsh@redhat.com> 0.77-39
- Change to only report failure on relabel if debug

* Wed Mar 3 2004 Dan Walsh <dwalsh@redhat.com> 0.77-38
- Fix error handling of pam_unix

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb 26 2004 Dan Walsh <dwalsh@redhat.com> 0.77-36
- fix tty handling

* Thu Feb 26 2004 Dan Walsh <dwalsh@redhat.com> 0.77-35
- remove tty closing and opening from pam_selinux, it does not work.

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 12 2004 Nalin Dahyabhai <nalin@redhat.com>
- pam_unix: also log successful password changes when using shadowed passwords

* Tue Feb 10 2004 Dan Walsh <dwalsh@redhat.com> 0.77-33
- close and reopen terminal after changing context.

* Thu Feb 5 2004 Dan Walsh <dwalsh@redhat.com> 0.77-32
- Check for valid tty

* Tue Feb 3 2004 Dan Walsh <dwalsh@redhat.com> 0.77-31
- Check for multiple > 1

* Mon Feb 2 2004 Dan Walsh <dwalsh@redhat.com> 0.77-30
- fix is_selinux_enabled call for pam_rootok

* Wed Jan 28 2004 Dan Walsh <dwalsh@redhat.com> 0.77-29
- More fixes to pam_selinux,pam_rootok

* Wed Jan 28 2004 Dan Walsh <dwalsh@redhat.com> 0.77-28
- turn on selinux

* Wed Jan 28 2004 Dan Walsh <dwalsh@redhat.com> 0.77-27
- Fix rootok check.

* Mon Jan 26 2004 Dan Walsh <dwalsh@redhat.com> 0.77-26
- fix is_selinux_enabled call

* Sun Jan 25 2004 Dan Walsh <dwalsh@redhat.com> 0.77-25
- Check if ROOTOK for SELinux

* Thu Jan 15 2004 Dan Walsh <dwalsh@redhat.com> 0.77-24
- Fix tty handling for pts in pam_selinux

* Thu Jan 15 2004 Dan Walsh <dwalsh@redhat.com> 0.77-23
- Need to add qualifier context for sudo situation

* Thu Jan 15 2004 Dan Walsh <dwalsh@redhat.com> 0.77-22
- Fix pam_selinux to use prevcon instead of pam_user so it will work for su.

* Fri Dec 12 2003 Bill Nottingham <notting@redhat.com> 0.77-21.sel
- add alsa devs to console.perms

* Thu Dec 11 2003 Jeff Johnson <jbj@jbj.org> 0.77-20.sel
- rebuild with db-4.2.52.
- build db4 in build_unix, not dist.

* Wed Nov 26 2003 Dan Walsh <dwalsh@redhat.com> 0.77-19.sel
- Change unix_chkpwd to handle unix_passwd and unix_acct
- This eliminates the need for pam modules to have read/write access to /etc/shadow.

* Thu Nov 20 2003 Dan Walsh <dwalsh@redhat.com> 0.77-18.sel
- Cleanup unix_chkpwd

* Mon Nov 03 2003 Dan Walsh <dwalsh@redhat.com> 0.77-17.sel
- Fix tty handling 
- Add back multiple handling

* Mon Oct 27 2003 Dan Walsh <dwalsh@redhat.com> 0.77-16.sel
- Remove Multiple from man page of pam_selinux

* Thu Oct 23 2003 Nalin Dahyabhai <nalin@redhat.com> 0.77-15
- don't install _pam_aconf.h -- apps don't use it, other PAM headers which
  are installed don't use it, and its contents may be different for arches
  on a multilib system
- check for linkage problems in modules at %%install-time (kill #107093 dead)
- add buildprereq on flex (#101563)

* Wed Oct 22 2003 Nalin Dahyabhai <nalin@redhat.com>
- make pam_pwdb.so link with libnsl again so that it loads (#107093)
- remove now-bogus buildprereq on db4-devel (we use a bundled copy for
  pam_userdb to avoid symbol collisions with other db libraries in apps)

* Mon Oct 20 2003 Dan Walsh <dwalsh@redhat.com> 0.77-14.sel
- Add Russell Coker patch to handle /dev/pty

* Fri Oct 17 2003 Dan Walsh <dwalsh@redhat.com> 0.77-13.sel
- Turn on Selinux 

* Fri Oct 17 2003 Dan Walsh <dwalsh@redhat.com> 0.77-12
- Fix pam_timestamp to work when 0 seconds have elapsed

* Mon Oct 6 2003 Dan Walsh <dwalsh@redhat.com> 0.77-11
- Turn off selinux

* Thu Sep 25 2003 Dan Walsh <dwalsh@redhat.com> 0.77-10.sel
- Turn on Selinux and remove multiple choice of context.  

* Wed Sep 24 2003 Dan Walsh <dwalsh@redhat.com> 0.77-10
- Turn off selinux

* Wed Sep 24 2003 Dan Walsh <dwalsh@redhat.com> 0.77-9.sel
- Add Russell's patch to check password

* Wed Sep 17 2003 Dan Walsh <dwalsh@redhat.com> 0.77-8.sel
- handle ttys correctly in pam_selinux

* Fri Sep 05 2003 Dan Walsh <dwalsh@redhat.com> 0.77-7.sel
- Clean up memory problems and fix tty handling.

* Mon Jul 28 2003 Dan Walsh <dwalsh@redhat.com> 0.77-6
- Add manual context selection to pam_selinux

* Mon Jul 28 2003 Dan Walsh <dwalsh@redhat.com> 0.77-5
- Add pam_selinux

* Mon Jul 28 2003 Dan Walsh <dwalsh@redhat.com> 0.77-4
- Add SELinux support

* Thu Jul 24 2003 Nalin Dahyabhai <nalin@redhat.com> 0.77-3
- pam_postgresok: add
- pam_xauth: add "targetuser" argument

* Tue Jul 22 2003 Nalin Dahyabhai <nalin@redhat.com>
- pam_succeed_if: fix thinko in argument parsing which would walk past the
  end of the argument list

* Wed Jul  9 2003 Nalin Dahyabhai <nalin@redhat.com> 0.77-2
- reapply:
  - set handler for SIGCHLD to SIG_DFL around *_chkpwd, not SIG_IGN

* Mon Jul  7 2003 Nalin Dahyabhai <nalin@redhat.com> 0.77-1
- pam_timestamp: fail if the key file doesn't contain enough data

* Thu Jul  3 2003 Nalin Dahyabhai <nalin@redhat.com> 0.77-0
- update to 0.77 upstream release
  - pam_limits: limits now affect root as well
  - pam_nologin: returns PAM_IGNORE instead of PAM_SUCCESS unless "successok"
    is given as an argument
  - pam_userdb: correctly return PAM_AUTH_ERR instead of PAM_USER_UNKNOWN when
    invoked with the "key_only" argument and the database has an entry of the
    form "user-<wrongpassword>"
- use a bundled libdb for pam_userdb.so because the system copy uses threads,
  and demand-loading a shared library which uses threads into an application
  which doesn't is a Very Bad Idea

* Thu Jul  3 2003 Nalin Dahyabhai <nalin@redhat.com>
- pam_timestamp: use a message authentication code to validate timestamp files

* Mon Jun 30 2003 Nalin Dahyabhai <nalin@redhat.com> 0.75-48.1
- rebuild

* Mon Jun  9 2003 Nalin Dahyabhai <nalin@redhat.com> 0.75-49
- modify calls to getlogin() to check the directory of the current TTY before
  searching for an entry in the utmp/utmpx file (#98020, #98826, CAN-2003-0388)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Feb 10 2003 Bill Nottingham <notting@redhat.com> 0.75-48
- set handler for SIGCHLD to SIG_DFL around *_chkpwd, not SIG_IGN

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 0.75-47
- rebuilt

* Tue Dec 17 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-46
- pam_xauth: reintroduce ACL support, per the original white paper
- pam_xauth: default root's export ACL to none instead of everyone

* Mon Dec  2 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-45
- create /lib/security, even if it isn't /%%{_lib}/security, because we
  can't locate /lib/security/$ISA without it (noted by Arnd Bergmann)
- clear out the duplicate docs directory created during %%install

* Thu Nov 21 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-44
- fix syntax errors in pam_console's yacc parser which newer bison chokes on
- forcibly set FAKEROOT at make install time

* Tue Oct 22 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-43
- patch to interpret $ISA in case the fist module load attempt fails
- use $ISA in default configs

* Fri Oct 04 2002 Elliot Lee <sopwith@redhat.com> 0.75-42
- Since cracklib-dicts location will not be correctly detected without 
  that package being installed, add buildreq for cracklib-dicts.
- Add patch57: makes configure use $LIBNAME when searching for cracklib 
  dicts, and error out if not found.

* Thu Sep 12 2002 Than Ngo <than@redhat.com> 0.75-41.1
- Fixed pam config files

* Wed Sep 11 2002 Than Ngo <than@redhat.com> 0.75-41
- Added fix to install libs in correct directory on 64bit machine

* Fri Aug  2 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-40
- pam_timestamp_check: check that stdio descriptors are open before we're
  invoked
- add missing chroot.conf

* Mon Jul 29 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-39
- pam_timestamp: sundry fixes, use "unknown" as the tty when none is found

* Thu Jun 27 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-38
- pam_timestamp_check: be as smart about figuring out the tty as the module is

* Wed Jun 19 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-37
- pam_timestamp_check: remove extra unlink() call spotted by Havoc

* Mon Jun 17 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-36
- pam_timestamp: chown intermediate directories when creating them
- pam_timestamp_check: add -d flag to poll

* Thu May 23 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-35
- pam_timestamp: add some sanity checks
- pam_timestamp_check: add

* Wed May 22 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-34
- pam_timestamp: add a 'verbose' option

* Thu May 16 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-33
- rebuild with db4
- just bundle install-sh into the source package

* Tue Apr  9 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-32
- pam_unix: be more compatible with AIX-style shadowing (#19236)

* Thu Mar 28 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-31
- libpam_misc: fix possible infinite loop in misc_conv (#62195)
- pam_xauth: fix cases where DISPLAY is "localhost:screen" and the xauth
  key is actually stored using the system's hostname (#61524)

* Mon Mar 25 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-30
- rebuild

* Mon Mar 25 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-29
- rebuild

* Mon Mar 11 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-28
- include the pwdb config file

* Fri Mar  1 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-27
- adjust the pwdb-static patch to build pam_radius correctly (#59408)

* Fri Mar  1 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-26
- change the db4-devel build dependency to db3-devel

* Thu Feb 21 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-25
- rebuild

* Fri Feb  8 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-24
- pam_unix: log successful password changes
- remove pam_timestamp

* Thu Feb  7 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-23
- fix pwdb embedding
- add pam_timestamp

* Thu Jan 31 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-22
- swallow up pwdb 0.61.1 for building pam_pwdb

* Wed Jan 23 2002 Nalin Dahyabhai <nalin@redhat.com> 0.75-21
- pam_userdb: build with db4 instead of db3

* Wed Nov 22 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-20
- pam_stack: fix some memory leaks (reported by Fernando Trias)
- pam_chroot: integrate Owl patch to report the more common causes of failures

* Fri Nov  9 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-19
- fix a bug in the getpwnam_r wrapper which sometimes resulted in false
  positives for non-existent users

* Wed Nov  7 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-18
- include libpamc in the pam package (#55651)

* Fri Nov  2 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-17
- pam_xauth: don't free a string after passing it to putenv()

* Wed Oct 24 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-16
- pam_xauth: always return PAM_SUCCESS or PAM_SESSION_ERR instead of PAM_IGNORE,
  matching the previous behavior (libpam treats PAM_IGNORE from a single module
  in a stack as a session error, leading to false error messages if we just
  return PAM_IGNORE for all cases)

* Mon Oct 22 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-15
- reorder patches so that the reentrancy patch is applied last -- we never
  came to a consensus on how to guard against the bugs in calling applications
  which this sort of change addresses, and having them last allows for dropping
  in a better strategy for addressing this later on

* Mon Oct 15 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_rhosts: allow "+hostname" as a synonym for "hostname" to jive better
  with the hosts.equiv(5) man page
- use the automake install-sh instead of the autoconf install-sh, which
  disappeared somewhere between 2.50 and now

* Mon Oct  8 2001 Nalin Dahyabhai <nalin@redhat.com>
- add pwdb as a buildprereq

* Fri Oct  5 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_tally: don't try to read past the end of faillog -- it probably contains
  garbage, which if written into the file later on will confuse /usr/bin/faillog

* Thu Oct  4 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_limits: don't just return if the user is root -- we'll want to set the
  priority (it could be negative to elevate root's sessions)
- pam_issue: fix off-by-one error allocating space for the prompt string

* Wed Oct  3 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_mkhomedir: recurse into subdirectories properly
- pam_mkhomedir: handle symlinks
- pam_mkhomedir: skip over special items in the skeleton directory

* Tue Oct  2 2001 Nalin Dahyabhai <nalin@redhat.com>
- add cracklib as a buildprereq
- pam_wheel: don't ignore out if the user is attempting to switch to a
  unprivileged user (this lets pam_wheel do its thing when users attempt
  to get to system accounts or accounts of other unprivileged users)

* Fri Sep 28 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_xauth: close a possible DoS due to use of dotlock-style locking in
  world-writable directories by relocating the temporary file to the target
  user's home directory
- general: include headers local to this tree using relative paths so that
  system headers for PAM won't be pulled in, in case include paths don't
  take care of it

* Thu Sep 27 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_xauth: rewrite to skip refcounting and just use a temporary file
  created using mkstemp() in /tmp

* Tue Sep 25 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_userdb: fix the key_only flag so that the null-terminator of the
  user-password string isn't expected to be part of the key in the db file,
  matching the behavior of db_load 3.2.9

* Mon Sep 24 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_unix: use crypt() instead of bigcrypt() when salted field is less than
  the critical size which lets us know it was generated with bigcrypt()
- use a wrapper to handle ERANGE errors when calling get....._r functions:
  defining PAM_GETPWNAM_R and such (for getpwnam, getpwuid, getgrnam,
  getgrgid, and getspnam) before including _pam_macros.h will cause them
  to be implemented as static functions, similar to how defining PAM_SM_xxx
  is used to control whether or not PAM declares prototypes for certain
  functions

* Mon Sep 24 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-14
- pam_unix: argh, compare entire pruned salt string with crypted result, always

* Sat Sep  8 2001 Bill Nottingham <notting@redhat.com> 0.75-13
- ship /lib/lib{pam,pam_misc}.so for legacy package builds

* Thu Sep  6 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-12
- noreplace configuration files in /etc/security
- pam_console: update pam_console_apply and man pages to reflect
  /var/lock -> /var/run move

* Wed Sep  5 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-11
- pam_unix: fix the fix for #42394

* Tue Sep  4 2001 Nalin Dahyabhai <nalin@redhat.com>
- modules: use getpwnam_r and friends instead of non-reentrant versions
- pam_console: clear generated .c and .h files in "clean" makefile target

* Thu Aug 30 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_stack: perform deep copy of conversation structures
- include the static libpam in the -devel subpackage (#52321)
- move development .so and .a files to %%{_libdir}
- pam_unix: don't barf on empty passwords (#51846)
- pam_unix: redo compatibility with "hash,age" data wrt bigcrypt (#42394)
- console.perms: add usb camera, scanner, and rio devices (#15528)
- pam_cracklib: initialize all options properly (#49613)

* Wed Aug 22 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_limits: don't rule out negative priorities

* Mon Aug 13 2001 Nalin Dahyabhai <nalin@redhat.com> 0.75-10
- pam_xauth: fix errors due to uninitialized data structure (fix from Tse Huong
  Choo)
- pam_xauth: random cleanups
- pam_console: use /var/run/console instead of /var/lock/console at install-time
- pam_unix: fix preserving of permissions on files which are manipulated

* Fri Aug 10 2001 Bill Nottingham <notting@redhat.com>
- fix segfault in pam_securetty

* Thu Aug  9 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_console: use /var/run/console instead of /var/lock/console for lock files
- pam_issue: read the right number of bytes from the file

* Mon Jul  9 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_wheel: don't error out if the group has no members, but is the user's
  primary GID (reported by David Vos)
- pam_unix: preserve permissions on files which are manipulated (#43706)
- pam_securetty: check if the user is the superuser before checking the tty,
  thereby allowing regular users access to services which don't set the
  PAM_TTY item (#39247)
- pam_access: define NIS and link with libnsl (#36864)

* Thu Jul  5 2001 Nalin Dahyabhai <nalin@redhat.com>
- link libpam_misc against libpam

* Tue Jul  3 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_chroot: chdir() before chroot()

* Fri Jun 29 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_console: fix logic bug when changing permissions on single
  file and/or lists of files
- pam_console: return the proper error code (reported and patches
  for both from Frederic Crozat)
- change deprecated Copyright: tag in .spec file to License:

* Mon Jun 25 2001 Nalin Dahyabhai <nalin@redhat.com>
- console.perms: change js* to js[0-9]*
- include pam_aconf.h in more modules (patches from Harald Welte)

* Thu May 24 2001 Nalin Dahyabhai <nalin@redhat.com>
- console.perms: add apm_bios to the list of devices the console owner can use
- console.perms: add beep to the list of sound devices

* Mon May  7 2001 Nalin Dahyabhai <nalin@redhat.com>
- link pam_console_apply statically with libglib (#38891)

* Mon Apr 30 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_access: compare IP addresses with the terminating ".", as documented
  (patch from Carlo Marcelo Arenas Belon, I think) (#16505)

* Mon Apr 23 2001 Nalin Dahyabhai <nalin@redhat.com>
- merge up to 0.75
- pam_unix: temporarily ignore SIGCHLD while running the helper
- pam_pwdb: temporarily ignore SIGCHLD while running the helper
- pam_dispatch: default to uncached behavior if the cached chain is empty

* Fri Apr  6 2001 Nalin Dahyabhai <nalin@redhat.com>
- correct speling errors in various debug messages and doc files (#33494)

* Thu Apr  5 2001 Nalin Dahyabhai <nalin@redhat.com>
- prereq sed, fileutils (used in %%post)

* Wed Apr  4 2001 Nalin Dahyabhai <nalin@redhat.com>
- remove /dev/dri from console.perms -- XFree86 munges it, so it's outside of
  our control (reminder from Daryll Strauss)
- add /dev/3dfx to console.perms

* Fri Mar 23 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_wheel: make 'trust' and 'deny' work together correctly
- pam_wheel: also check the user's primary gid
- pam_group: also initialize groups when called with PAM_REINITIALIZE_CRED

* Tue Mar 20 2001 Nalin Dahyabhai <nalin@redhat.com>
- mention pam_console_apply in the see also section of the pam_console man pages

* Fri Mar 16 2001 Nalin Dahyabhai <nalin@redhat.com>
- console.perms: /dev/vc/* should be a regexp, not a glob (thanks to
  Charles Lopes)

* Mon Mar 12 2001 Nalin Dahyabhai <nalin@redhat.com>
- console.perms: /dev/cdroms/* should belong to the user, from Douglas
  Gilbert via Tim Waugh

* Thu Mar  8 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_console_apply: muck with devices even if the mount point doesn't exist

* Wed Mar  7 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_console: error out on undefined classes in pam_console config file
- console.perms: actually change the permissions on the new device classes
- pam_console: add an fstab= argument, and -f and -c flags to pam_console_apply
- pam_console: use g_log instead of g_critical when bailing out
- console.perms: logins on /dev/vc/* are also console logins, from Douglas
  Gilbert via Tim Waugh

* Tue Mar  6 2001 Nalin Dahyabhai <nalin@redhat.com>
- add pam_console_apply
- /dev/pilot's usually a serial port (or a USB serial port), so revert its
  group to 'uucp' instead of 'tty' in console.perms
- change pam_console's behavior wrt directories -- directories which are
  mount points according to /etc/fstab are taken to be synonymous with
  their device special nodes, and directories which are not mount points
  are ignored

* Tue Feb 27 2001 Nalin Dahyabhai <nalin@redhat.com>
- handle errors fork()ing in pam_xauth
- make the "other" config noreplace

* Mon Feb 26 2001 Nalin Dahyabhai <nalin@redhat.com>
- user should own the /dev/video directory, not the non-existent /dev/v4l
- tweak pam_limits doc

* Wed Feb 21 2001 Nalin Dahyabhai <nalin@redhat.com>
- own /etc/security
- be more descriptive when logging messages from pam_limits
- pam_listfile: remove some debugging code (#28346)

* Mon Feb 19 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_lastlog: don't pass NULL to logwtmp()

* Fri Feb 16 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_listfile: fix argument parser (#27773)
- pam_lastlog: link to libutil

* Tue Feb 13 2001 Nalin Dahyabhai <nalin@redhat.com>
- pam_limits: change the documented default config file to reflect the defaults
- pam_limits: you should be able to log in a total of maxlogins times, not
  (maxlogins - 1)
- handle group limits on maxlogins correctly (#25690)

* Mon Feb 12 2001 Nalin Dahyabhai <nalin@redhat.com>
- change the pam_xauth default maximum "system user" ID from 499 to 99 (#26343)

* Wed Feb  7 2001 Nalin Dahyabhai <nalin@redhat.com>
- refresh the default system-auth file, pam_access is out

* Mon Feb  5 2001 Nalin Dahyabhai <nalin@redhat.com>
- actually time out when attempting to lckpwdf() (#25889)
- include time.h in pam_issue (#25923)
- update the default system-auth to the one generated by authconfig 4.1.1
- handle getpw??? and getgr??? failures more gracefully (#26115)
- get rid of some extraneous {set,end}{pw,gr}ent() calls

* Tue Jan 30 2001 Nalin Dahyabhai <nalin@redhat.com>
- overhaul pam_stack to account for abstraction libpam now provides

* Tue Jan 23 2001 Nalin Dahyabhai <nalin@redhat.com>
- remove pam_radius at request of author

* Mon Jan 22 2001 Nalin Dahyabhai <nalin@redhat.com>
- merge to 0.74
- make console.perms match perms set by MAKEDEV, and add some devfs device names
- add 'sed' to the buildprereq list (#24666)

* Sun Jan 21 2001 Matt Wilson <msw@redhat.com>
- added "exit 0" to the end of the %pre script

* Fri Jan 19 2001 Nalin Dahyabhai <nalin@redhat.com>
- self-hosting fix from Guy Streeter

* Wed Jan 17 2001 Nalin Dahyabhai <nalin@redhat.com>
- use gcc for LD_L to pull in intrinsic stuff on ia64

* Fri Jan 12 2001 Nalin Dahyabhai <nalin@redhat.com>
- take another whack at compatibility with "hash,age" data in pam_unix (#21603)

* Wed Jan 10 2001 Nalin Dahyabhai <nalin@redhat.com>
- make the -devel subpackage unconditional

* Tue Jan  9 2001 Nalin Dahyabhai <nalin@redhat.com>
- merge/update to 0.73

* Mon Dec 18 2000 Nalin Dahyabhai <nalin@redhat.com>
- refresh from CVS -- some weird stuff crept into pam_unix

* Wed Dec 12 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix handling of "nis" when changing passwords by adding the checks for the
  data source to the password-updating module in pam_unix
- add the original copyright for pam_access (fix from Michael Gerdts)

* Thu Nov 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- redo similar() using a distance algorithm and drop the default dif_ok to 5
- readd -devel

* Wed Nov 29 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix similar() function in pam_cracklib (#14740)
- fix example in access.conf (#21467)
- add conditional compilation for building for 6.2 (for pam_userdb)
- tweak post to not use USESHADOW any more

* Tue Nov 28 2000 Nalin Dahyabhai <nalin@redhat.com>
- make EINVAL setting lock limits in pam_limits non-fatal, because it's a 2.4ism

* Tue Nov 21 2000 Nalin Dahyabhai <nalin@redhat.com>
- revert to DB 3.1, which is what we were supposed to be using from the get-go

* Mon Nov 20 2000 Nalin Dahyabhai <nalin@redhat.com>
- add RLIMIT_LOCKS to pam_limits (patch from Jes Sorensen) (#20542)
- link pam_userdb to Berkeley DB 2.x to match 6.2's setup correctly

* Mon Nov  6 2000 Matt Wilson <msw@redhat.com>
- remove prereq on sh-utils, test ([) is built in to bash

* Thu Oct 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix the pam_userdb module breaking

* Wed Oct 18 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix pam_unix likeauth argument for authenticate(),setcred(),setcred()

* Tue Oct 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- tweak pre script to be called in all upgrade cases
- get pam_unix to only care about the significant pieces of passwords it checks
- add /usr/include/db1/db.h as a build prereq to pull in the right include
  files, no matter whether they're in glibc-devel or db1-devel
- pam_userdb.c: include db1/db.h instead of db.h

* Wed Oct 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- add BuildPrereq for bison (suggested by Bryan Stillwell)

* Fri Oct  6 2000 Nalin Dahyabhai <nalin@redhat.com>
- patch from Dmitry V. Levin to have pam_stack propagate the PAM fail_delay
- roll back the README for pam_xauth to actually be the right one
- tweak pam_stack to use the parent's service name when calling the substack

* Wed Oct  4 2000 Nalin Dahyabhai <nalin@redhat.com>
- create /etc/sysconfig/authconfig at install-time if upgrading

* Mon Oct  2 2000 Nalin Dahyabhai <nalin@redhat.com>
- modify the files list to make sure #16456 stays fixed
- make pam_stack track PAM_AUTHTOK and PAM_OLDAUTHTOK items
- add pam_chroot module
- self-hosting fixes from the -devel split
- update generated docs in the tree

* Tue Sep 12 2000 Nalin Dahyabhai <nalin@redhat.com>
- split off a -devel subpackage
- install the developer man pages

* Sun Sep 10 2000 Bill Nottingham <notting@redhat.com>
- build libraries before modules

* Wed Sep  6 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix problems when looking for headers in /usr/include (#17236)
- clean up a couple of compile warnings

* Tue Aug 22 2000 Nalin Dahyabhai <nalin@redhat.com>
- give users /dev/cdrom* instead of /dev/cdrom in console.perms (#16768)
- add nvidia control files to console.perms

* Tue Aug 22 2000 Bill Nottingham <notting@redhat.com>
- add DRI devices to console.perms (#16731)

* Thu Aug 17 2000 Nalin Dahyabhai <nalin@redhat.com>
- move pam_filter modules to /lib/security/pam_filter (#16111)
- add pam_tally's application to allow counts to be reset (#16456)
- move README files to the txts subdirectory

* Mon Aug 14 2000 Nalin Dahyabhai <nalin@redhat.com>
- add a postun that runs ldconfig
- clean up logging in pam_xauth

* Fri Aug  4 2000 Nalin Dahyabhai <nalin@redhat.com>
- make the tarball include the release number in its name

* Mon Jul 31 2000 Nalin Dahyabhai <nalin@redhat.com>
- add a broken_shadow option to pam_unix
- add all module README files to the documentation list (#16456)

* Wed Jul 25 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix pam_stack debug and losing-track-of-the-result bug

* Tue Jul 24 2000 Nalin Dahyabhai <nalin@redhat.com>
- rework pam_console's usage of syslog to actually be sane (#14646)

* Sat Jul 22 2000 Nalin Dahyabhai <nalin@redhat.com>
- take the LOG_ERR flag off of some of pam_console's new messages

* Fri Jul 21 2000 Nalin Dahyabhai <nalin@redhat.com>
- add pam_localuser

* Wed Jul 12 2000 Nalin Dahyabhai <nalin@redhat.com>
- need to make pam_console's checking a little stronger
- only pass data up from pam_stack if the parent didn't already define it

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Tue Jul 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- make pam_console's extra checks disableable
- simplify extra check to just check if the device owner is root
- add a debug log when pam_stack comes across a NULL item
- have pam_stack hand items up to the parent from the child

* Mon Jul  3 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix installation of pam_xauth man pages (#12417)
- forcibly strip helpers (#12430)
- try to make pam_console a little more discriminating

* Mon Jun 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- symlink libpam.so to libpam.so.%{version}, and likewise for libpam_misc
- reverse order of checks in _unix_getpwnam for pam_unix

* Wed Jun 14 2000 Preston Brown <pbrown@redhat.com>
- include gpmctl in pam_console

* Mon Jun 05 2000 Nalin Dahyabhai <nalin@redhat.com>
- add MANDIR definition and use it when installing man pages

* Mon Jun 05 2000 Preston Brown <pbrown@redhat.com>
- handle scanner and cdwriter devices in pam_console

* Sat Jun  3 2000 Nalin Dahyabhai <nalin@redhat.com>
- add account management wrappers for pam_listfile, pam_nologin, pam_securetty,
  pam_shells, and pam_wheel

* Thu Jun  1 2000 Nalin Dahyabhai <nalin@redhat.com>
- add system-auth control file
- let gethostname() call in pam_access.c be implicitly declared to avoid
  conflicting types if unistd.c declares it

* Mon May 15 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix problems compiling on Red Hat Linux 5.x (bug #11005)

* Wed Apr 26 2000 Bill Nottingham <notting@redhat.com>
- fix size assumptions in pam_(pwdb|unix) md5 code

* Mon Mar 20 2000 Nalin Dahyabhai <nalin@redhat.com>
- Add new pam_stack module.
- Install pwdb_chkpwd and unix_chkpwd as the current user for non-root builds

* Sat Feb 05 2000 Nalin Dahyabhai <nalin@redhat.com>
- Fix pam_xauth bug #6191.

* Thu Feb 03 2000 Elliot Lee <sopwith@redhat.com>
- Add a patch to accept 'pts/N' in /etc/securetty as a match for tty '5'
  (which is what other pieces of the system think it is). Fixes bug #7641.

* Mon Jan 31 2000 Nalin Dahyabhai <nalin@redhat.com>
- argh, turn off gratuitous debugging

* Wed Jan 19 2000 Nalin Dahyabhai <nalin@redhat.com>
- update to 0.72
- fix pam_unix password-changing bug
- fix pam_unix's cracklib support
- change package URL

* Mon Jan 03 2000 Cristian Gafton <gafton@redhat.com>
- don't allow '/' on service_name

* Thu Oct 21 1999 Cristian Gafton <gafton@redhat.com>
- enhance the pam_userdb module some more

* Fri Sep 24 1999 Cristian Gafton <gafton@redhat.com>
- add documenatation

* Tue Sep 21 1999 Michael K. Johnson <johnsonm@redhat.com>
- a tiny change to pam_console to make it not loose track of console users

* Mon Sep 20 1999 Michael K. Johnson <johnsonm@redhat.com>
- a few fixes to pam_xauth to make it more robust

* Wed Jul 14 1999 Michael K. Johnson <johnsonm@redhat.com>
- pam_console: added <xconsole> to manage /dev/console

* Thu Jul 01 1999 Michael K. Johnson <johnsonm@redhat.com>
- pam_xauth: New refcounting implementation based on idea from Stephen Tweedie

* Sat Apr 17 1999 Michael K. Johnson <johnsonm@redhat.com>
- added video4linux devices to /etc/security/console.perms

* Fri Apr 16 1999 Michael K. Johnson <johnsonm@redhat.com>
- added joystick lines to /etc/security/console.perms

* Thu Apr 15 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed a couple segfaults in pam_xauth uncovered by yesterday's fix...

* Wed Apr 14 1999 Cristian Gafton <gafton@redhat.com>
- use gcc -shared to link the shared libs

* Wed Apr 14 1999 Michael K. Johnson <johnsonm@redhat.com>
- many bug fixes in pam_xauth
- pam_console can now handle broken applications that do not set
  the PAM_TTY item.

* Tue Apr 13 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed glob/regexp confusion in pam_console, added kbd and fixed fb devices
- added pam_xauth module

* Sat Apr 10 1999 Cristian Gafton <gafton@redhat.com>
- pam_lastlog does wtmp handling now

* Thu Apr 08 1999 Michael K. Johnson <johnsonm@redhat.com>
- added option parsing to pam_console
- added framebuffer devices to default console.perms settings

* Wed Apr 07 1999 Cristian Gafton <gafton@redhat.com>
- fixed empty passwd handling in pam_pwdb

* Mon Mar 29 1999 Michael K. Johnson <johnsonm@redhat.com>
- changed /dev/cdrom default user permissions back to 0600 in console.perms
  because some cdrom players open O_RDWR.

* Fri Mar 26 1999 Michael K. Johnson <johnsonm@redhat.com>
- added /dev/jaz and /dev/zip to console.perms

* Thu Mar 25 1999 Michael K. Johnson <johnsonm@redhat.com>
- changed the default user permissions for /dev/cdrom to 0400 in console.perms

* Fri Mar 19 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed a few bugs in pam_console

* Thu Mar 18 1999 Michael K. Johnson <johnsonm@redhat.com>
- pam_console authentication working
- added /etc/security/console.apps directory

* Mon Mar 15 1999 Michael K. Johnson <johnsonm@redhat.com>
- added pam_console files to filelist

* Fri Feb 12 1999 Cristian Gafton <gafton@redhat.com>
- upgraded to 0.66, some source cleanups

* Mon Dec 28 1998 Cristian Gafton <gafton@redhat.com>
- add patch from Savochkin Andrey Vladimirovich <saw@msu.ru> for umask
  security risk

* Fri Dec 18 1998 Cristian Gafton <gafton@redhat.com>
- upgrade to ver 0.65
- build the package out of internal CVS server
