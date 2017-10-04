#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /CoreOS/pam/Sanity/pam_unix
#   Description: Test for module pam_unix
#   Author: David Spurek <dspurek@redhat.com>
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
. /usr/share/beakerlib/beakerlib.sh

PACKAGE="pam"

PACKAGES=( "pam" "expect" )

_PASSWORD1="jf@#Faffo"
_PASSWORD2="0m4nchU!!F"

function do_passwd {
expect <<EOF
set timeout 5
spawn -noecho su $1 -c passwd
expect {
    timeout {puts timeout; exit 1}
    eof {exit 2}
    -nocase "(current)*password" { puts "$2"; send -- "$2\r"}
}
expect {
    timeout {puts timeout; exit 1}
    eof {exit 3}
    -nocase "new*password" { puts "$3"; send -- "$3\r"}
}
expect {
    timeout {puts timeout; exit 1}
    eof {exit 4}
    -nocase "has been already used" { puts "exit 6" ; exit 6}
    -nocase "retype*password" { puts "$3"; send -- "$3\r"}
}
expect {
    timeout {exit 5}
    -nocase "has been already used" { puts "exit 6" ; exit 6}
    eof
}
puts "end"
EOF
}


rlJournalStart && {
  rlPhaseStartSetup && {
    tcfTry "Setup phase" && {
      tcfRun "rlCheckMakefileRequires"
      rlRun "TmpDir=\$(mktemp -d)" 0 "Creating tmp directory"
      CleanupRegister "rlRun 'rm -r $TmpDir' 0 'Removing tmp directory'"
      CleanupRegister 'rlRun "popd"'
      rlRun "pushd $TmpDir"
      CleanupRegister 'rlRun "pamCleanup"'
      rlRun "pamSetup"
      CleanupRegister 'rlRun "rlFileRestore"'
      rlFileBackup "/etc/security/opasswd" && >/etc/security/opasswd
    tcfFin; }
  rlPhaseEnd; }

  tcfTry "Tests" --no-assert && {
    tcfChk && {
     rlPhaseStartTest "test option remember" && {
      tcfChk "setup" && {
        CleanupRegister --mark 'rlRun "testUserCleanup"'
        rlRun "testUserSetup 2"
        PWA=( ':3533tjh^397*:~21081^*p@w!~18374_0' ':4273tjh^397*:~3709^*p@w!~19467_1' ':31388tjh^397*:~32486^*p@w!~12258_2' ':10233tjh^397*:~620^*p@w!~19779_3' ':26151tjh^397*:~8077^*p@w!~29968_4' ':26593tjh^397*:~4665^*p@w!~16428_5' ':23163tjh^397*:~16784^*p@w!~4822_6' ':4065tjh^397*:~14355^*p@w!~4119_7' ':16312tjh^397*:~30577^*p@w!~26223_8' )
        rlRun "echo ${PWA[0]} | passwd --stdin ${testUser[1]}"
        CleanupRegister 'rlRun "pamRestoreFiles"'
        rlRun "pamBackupFiles"
        #rlRun "sed -i -e 's/^password\s\+sufficient\s\+pam_unix.so/\0 remember=5/' $sys_auth"
        rlRun "pamReplaceServiceModuleRule su password pam_unix.so '' '' '' '$(pamGetServiceRuleAgruments su password pam_unix.so) remember=5'"
        #rlRun "cat $sys_auth"
        rlRun "pamGetServiceRules --prefix su password"
      tcfFin; }

      tcfTry "test remember option" && {
        NEWPW=${PWA[0]}
        for i in `seq 6`; do
          rlLog "change passwrd #$i"
          OLDPW=$NEWPW; NEWPW=${PWA[$i]}
          rlRun "do_passwd ${testUser[1]} ${OLDPW} ${NEWPW}" 0
        done

        rlLog "change passwrd #$i"
        rlLog "Try change to password that have been alredy used (should fail)"
        OLDPW=$NEWPW;
        rlRun "do_passwd ${testUser[1]} ${OLDPW} ${PWA[1]}" 6

        for i in 7 8 1; do
          rlLog "change passwrd #$i"
          OLDPW=$NEWPW; NEWPW=${PWA[$i]}
          rlRun "do_passwd ${testUser[1]} ${OLDPW} ${NEWPW}" 0
        done
      tcfFin; }

      tcfTry "test vhange the password to a previous password of test1" && {
        # change the password to a previous password of test1, the password change should be allowed.
        rlLog "Change the password to a previous password of test1, the password change should be allowed"
        echo ${PWA[0]} | passwd --stdin $testUser
        rlRun "do_passwd $testUser ${PWA[0]} ${PWA[5]}" 0
      tcfFin; }

      tcfChk "cleanup" && {
        CleanupDo --mark
      tcfFin; }
     rlPhaseEnd; }; :
    tcfFin; }

    # Run the test for >=RHEL-6.9 and >=RHEL-7.3 and <>RHEL(Fedora)
    ! rlIsRHEL '<6.9' && { ! rlIsRHEL '<7.3' || rlIsRHEL 6; } && tcfChk && {
     rlPhaseStartTest "test option no_pass_expiry" && {
      tcfChk "setup" && {
        CleanupRegister --mark 'rlRun "testUserCleanup"'
        rlRun "testUserSetup"
        CleanupRegister 'rlRun "sshCleanup"'
        rlRun "sshSetup"
        rlRun "sshKeyGen"
        rlRun "sshCopyID --user $testUser --password $testUserPasswd"
        CleanupRegister 'rlRun "sshdRestore"'
        rlRun "sshdStart"
        CleanupRegister 'rlRun "pamRestoreFiles"'
        rlRun "pamBackupFiles"
        rlRun "pamGetServiceRules --prefix su account"
      tcfFin; }

      tcfTry "test" && {
        rlRun "sshRun --user $testUser --key 'id'"
        rlRun "chage -d 0 $testUser"
        rlRun "sshRun --user $testUser --key 'id'" 1-255
        rlRun "pamReplaceServiceModuleRule sshd account pam_unix.so '' '' '' '$(pamGetServiceRuleAgruments su password pam_unix.so) no_pass_expiry'"
        rlRun "pamGetServiceRules --prefix sshd account"
        rlRun "sshRun --user $testUser --key 'id'"
      tcfFin; }

      tcfChk "cleanup" && {
        CleanupDo --mark
      tcfFin; }
     rlPhaseEnd; }; :
    tcfFin; }; :
  tcfFin; }

  rlPhaseStartCleanup && {
    tcfChk "Cleanup phase" && {
      CleanupDo
    tcfFin; }
    tcfCheckFinal
  rlPhaseEnd; }
  rlJournalPrintText
rlJournalEnd; }
