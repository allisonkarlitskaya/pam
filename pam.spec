Summary: A security tool which provides authentication for applications.
Name: pam
Version: 0.72
Release: 26
Copyright: GPL or BSD
Group: System Environment/Base
Source0: pam-redhat-%{version}-%{release}.tar.gz
Source1: other.pamd
BuildRoot: %{_tmppath}/%{name}-root
Requires: cracklib, cracklib-dicts, pwdb >= 0.54-2, initscripts >= 3.94
Obsoletes: pamconfig
Url: http://www.us.kernel.org/pub/linux/libs/pam/index.html

%description
PAM (Pluggable Authentication Modules) is a system security tool
which allows system administrators to set authentication policy
without having to recompile programs which do authentication.

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

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%dir /etc/pam.d
%config /etc/pam.d/other
%config(noreplace) /etc/pam.d/system-auth
%doc Copyright
%doc doc/html doc/ps doc/txts
%doc doc/specs/rfc86.0.txt
/lib/libpam.so*
/lib/libpam_misc.so*
/lib/libpam_misc.a
/usr/include/security/*.h
/sbin/*
/lib/security
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

%changelog
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

