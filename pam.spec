%define build6x 0
%define builddevel 0
Summary: A security tool which provides authentication for applications.
Name: pam
Version: 0.72
Release: 37
Copyright: GPL or BSD
Group: System Environment/Base
Source0: pam-redhat-%{version}-%{release}.tar.gz
Source1: other.pamd
BuildRoot: %{_tmppath}/%{name}-root
Requires: cracklib, cracklib-dicts, glib, pwdb >= 0.54-2, initscripts >= 3.94
Obsoletes: pamconfig
Prereq: grep, mktemp, textutils, /sbin/ldconfig
BuildPrereq: bison, glib-devel
%if ! %{build6x}
BuildPrereq: db3-devel
%endif
URL: http://www.us.kernel.org/pub/linux/libs/pam/index.html

%description
PAM (Pluggable Authentication Modules) is a system security tool
which allows system administrators to set authentication policy
without having to recompile programs which do authentication.

%if %{builddevel}
%package devel
Group: Development/Libraries
Summary: Files needed for developing PAM-aware applications and modules for PAM.
Requires: pam = %{version}-%{release}

%description devel
PAM (Pluggable Authentication Modules) is a system security tool
which allows system administrators to set authentication policy
without having to recompile programs which do authentication.  This
package contains header files and static libraries used for building
both PAM-aware applications and modules for use with PAM.
%endif

%prep
%setup -q
ln -sf defs/redhat.defs default.defs
for readme in modules/pam_*/README ; do
	cp -fv ${readme} doc/txts/README.`dirname ${readme} | sed -e 's|^modules/||'`
done

%build
touch .freezemake
make RPM_OPT_FLAGS="$RPM_OPT_FLAGS"

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/include/security
mkdir -p $RPM_BUILD_ROOT/lib/security
make install FAKEROOT=$RPM_BUILD_ROOT LDCONFIG=: MANDIR=%{_mandir}
install -d -m 755 $RPM_BUILD_ROOT/etc/pam.d
install -m 644 other.pamd $RPM_BUILD_ROOT/etc/pam.d/other
install -m 644 system-auth.pamd $RPM_BUILD_ROOT/etc/pam.d/system-auth
# make sure the modules built...
[ -f $RPM_BUILD_ROOT/lib/security/pam_deny.so ] || {
  echo "You have LITTLE or NOTHING in your /lib/security directory:"
  echo $RPM_BUILD_ROOT/lib/security/*
  echo ""
  echo "Fix it before you install this package, while you still can!"
  exit 1
}
# forcibly strip the helpers
strip $RPM_BUILD_ROOT/sbin/* ||:
# Install man pages.
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man3/
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8/
install -m 644 doc/man/*.3 $RPM_BUILD_ROOT%{_mandir}/man3/
install -m 644 doc/man/*.8 $RPM_BUILD_ROOT%{_mandir}/man8/

# Make sure every module built.
for dir in modules/pam_* ; do
if [ -d ${dir} ] ; then
	if ! ls -1 $RPM_BUILD_ROOT/lib/security/`basename ${dir}`*.so ; then
		echo ERROR `basename ${dir}` module did not build.
		exit 1
	fi
fi
done

%clean
rm -rf $RPM_BUILD_ROOT

%if ! %{build6x}
%pre
# Figure whether or not we're using shadow/md5 passwords if we're upgrading.
if [ -f /etc/pam.d/other ] ; then
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
%endif

%if %{build6x}
%post -p /sbin/ldconfig
%else
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
%endif

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%dir /etc/pam.d
%config /etc/pam.d/other
%config(noreplace) /etc/pam.d/system-auth
%doc Copyright
%doc doc/html doc/ps doc/txts
%doc doc/specs/rfc86.0.txt
/lib/libpam.so.*
/lib/libpam_misc.so.*
/sbin/*_chkpwd
/sbin/pam_tally
%dir /lib/security
/lib/security/pam_access.so
/lib/security/pam_chroot.so
/lib/security/pam_console.so
/lib/security/pam_cracklib.so
/lib/security/pam_deny.so
/lib/security/pam_env.so
/lib/security/pam_filter.so
/lib/security/pam_ftp.so
/lib/security/pam_group.so
/lib/security/pam_issue.so
/lib/security/pam_lastlog.so
/lib/security/pam_limits.so
/lib/security/pam_listfile.so
/lib/security/pam_localuser.so
/lib/security/pam_mail.so
/lib/security/pam_mkhomedir.so
/lib/security/pam_motd.so
/lib/security/pam_nologin.so
/lib/security/pam_permit.so
/lib/security/pam_pwdb.so
/lib/security/pam_radius.so
/lib/security/pam_rhosts_auth.so
/lib/security/pam_rootok.so
/lib/security/pam_securetty.so
/lib/security/pam_shells.so
/lib/security/pam_stack.so
/lib/security/pam_stress.so
/lib/security/pam_tally.so
/lib/security/pam_time.so
/lib/security/pam_unix.so
/lib/security/pam_unix_acct.so
/lib/security/pam_unix_auth.so
/lib/security/pam_unix_passwd.so
/lib/security/pam_unix_session.so
/lib/security/pam_userdb.so
/lib/security/pam_warn.so
/lib/security/pam_wheel.so
/lib/security/pam_xauth.so
/lib/security/pam_filter
%config /etc/security/access.conf
%config /etc/security/time.conf
%config /etc/security/group.conf
%config /etc/security/limits.conf
%config /etc/security/pam_env.conf
%config /etc/security/console.perms
%dir /etc/security/console.apps
%dir /var/lock/console
%{_mandir}/man5/*
%{_mandir}/man8/*

%if %{builddevel}
%files devel
%defattr(-,root,root)
%endif
/lib/libpam.so
/lib/libpam_misc.so
/lib/libpam_misc.a
/usr/include/security/
%{_mandir}/man3/*

%changelog
* Thu Nov 30 2000 Nalin Dahyabhai <nalin@redhat.com>
- redo similar() using a distance algorithm and drop the default dif_ok to 5

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

