%define build6x 0
Summary: A security tool which provides authentication for applications.
Name: pam
Version: 0.75
Release: 10
License: GPL or BSD
Group: System Environment/Base
Source0: pam-redhat-%{version}-%{release}.tar.gz
Source1: other.pamd
BuildRoot: %{_tmppath}/%{name}-root
Requires: cracklib, cracklib-dicts, glib, pwdb >= 0.54-2, initscripts >= 3.94
Obsoletes: pamconfig
Prereq: grep, mktemp, sed, fileutils, textutils, /sbin/ldconfig
BuildPrereq: bison, glib-devel, sed, fileutils, autoconf
%if ! %{build6x}
BuildPrereq: db3-devel
%endif
URL: http://www.us.kernel.org/pub/linux/libs/pam/index.html

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
%setup -q
for readme in modules/pam_*/README ; do
	cp -fv ${readme} doc/txts/README.`dirname ${readme} | sed -e 's|^modules/||'`
done
autoconf

%build
CFLAGS="$RPM_OPT_FLAGS -fPIC" \
./configure \
	--prefix=/ \
	--infodir=%{_infodir} \
	--mandir=%{_mandir} \
	--enable-static-libpam \
	--enable-fakeroot=$RPM_BUILD_ROOT
make

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
make install
install -d -m 755 $RPM_BUILD_ROOT/etc/pam.d
install -m 644 other.pamd $RPM_BUILD_ROOT/etc/pam.d/other
install -m 644 system-auth.pamd $RPM_BUILD_ROOT/etc/pam.d/system-auth

# forcibly strip the helpers
strip $RPM_BUILD_ROOT/sbin/* ||:

# Install man pages.
install -m 644 doc/man/*.3 $RPM_BUILD_ROOT%{_mandir}/man3/
install -m 644 doc/man/*.8 $RPM_BUILD_ROOT%{_mandir}/man8/

# Make sure every module built.  Yes, this is hackish.
for dir in modules/pam_* ; do
if [ -d ${dir} ] ; then
	if ! ls -1 $RPM_BUILD_ROOT/lib/security/`basename ${dir}`*.so ; then
		echo ERROR `basename ${dir}` module did not build.
		exit 1
	fi
fi
done

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

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
exit 0
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
%config(noreplace) /etc/pam.d/other
%config(noreplace) /etc/pam.d/system-auth
%doc Copyright
%doc doc/html doc/ps doc/txts
%doc doc/specs/rfc86.0.txt
/lib/libpam.so.*
/lib/libpam_misc.so.*
/sbin/*_chkpwd
/sbin/pam_console_apply
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
%dir /etc/security
%config /etc/security/access.conf
%config /etc/security/time.conf
%config /etc/security/group.conf
%config /etc/security/limits.conf
%config /etc/security/pam_env.conf
%config /etc/security/console.perms
%dir /etc/security/console.apps
%dir /var/run/console
%{_mandir}/man5/*
%{_mandir}/man8/*

%files devel
%defattr(-,root,root)
/lib/libpam.so
/lib/libpam_misc.so
/lib/libpam_misc.a
/usr/include/security/
%{_mandir}/man3/*

%changelog
* Mon Aug 13 2001 Nalin Dahyabhai <nalin@redhat.com>
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

