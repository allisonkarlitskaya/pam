#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /CoreOS/pam/Sanity/Test-coverage-for-TTY-auditing
#   Description: Test for Test coverage for TTY auditing
#   Author: Dalibor Pospisil <dapospis@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2012 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh
. /usr/lib/beakerlib/beakerlib.sh

PACKAGES="pam"
BINARIES="pcregrep expect bc"

rlJournalStart &&{
  rlPhaseStartSetup &&{
    rlTry "Setup phase" && {
      for PACKAGE in $PACKAGES; do
        rlAssertRpm $PACKAGE
      done
      for BINARY in $BINARIES; do
        rlRun "which $BINARY" 0 "Check presence of $BINARY"
      done
      rlRun "TmpDir=\$(mktemp -d)" 0 "Creating tmp directory"
      rlRun "pushd $TmpDir"
      rlFileBackup --clean /etc/pam.d/
      rlRun "echo 'session   required pam_tty_audit.so disable=* enable=root' >>/etc/pam.d/system-auth"
      rlRun "cat /etc/pam.d/system-auth"
    rlFin; }
  rlPhaseEnd;}

  rlPhaseStartTest &&{
    rlTry "Test phase" && {
      rlTry "backup audit.log" &&{
        cat /var/log/audit/audit.log >./audit.log
      rlFin; }
      unalias su >& /dev/null
      rlTry "su root, bc some expressions" &&{
        expect <<EOF
          set env(TERM) vt100
          set timeout 5
          spawn su -l root
          expect {
            timeout { exit 2 }
            eof { exit 1 }
            "#" { send -- "bc\r" }
          }
          expect -re "For details type .warranty.." { send -- "1+1\r" }
          expect {
            timeout { exit 2 }
            eof { exit 1 }
            "2" { send -- "10^2\r" }
          }
          expect {
            timeout { exit 2 }
            eof { exit 1 }
            "100" { send -- "\033\[A\033\[A\r" }
          }
          expect {
            timeout { exit 2 }
            eof { exit 1 }
            "2" { send -- "quit\r" }
          }
          expect {
            timeout { exit 2 }
            eof { exit 1 }
            "#" { send -- "exit\r" }
          }
          expect {
            timeout { exit 2 }
            eof { exit 0 }
          }
EOF
      rlFin; }
      rlTry &&{
        rlLog "wait 3s"
        sleep 3s
      rlFin; }
      rlRun "diff ./audit.log /var/log/audit/audit.log | grep '>' | sed -e 's/> //' | tee ./log" 0-255
      rlChk "check that audit.log contains what it should" &&{
        aureport --tty -ts recent -if ./log |tee log.txt
        rlRun "pcregrep -M 'bc \"1\+1\",(<ret>|<nl>)(\n|\r)?.*\"10\^2\",(<ret>|<nl>)(\r|\n)?.*<up>,<up>,(<ret>|<nl>)' log.txt"
      rlFin; }
    rlFin; }
    #PS1="[test] " bash
  rlPhaseEnd;}

  rlPhaseStartCleanup &&{
    rlChk "Cleanup phase" && {
      rlFileRestore
      rlRun "popd"
      rlRun "rm -r $TmpDir" 0 "Removing tmp directory"
    rlFin; }
    rlTCFcheckFinal
  rlPhaseEnd;}

  rlJournalPrintText
rlJournalEnd;}
