Name:       coreutils
Version:    8.32
Release:    3
License:    GPLv3+
Summary:    A set of basic GNU tools commonly used in shell scripts
Url:        https://www.gnu.org/software/coreutils/
Source0:    https://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz

# do not make coreutils-single depend on /usr/bin/coreutils
%global __requires_exclude ^%{_bindir}/coreutils$
%global user `ls -ld $USR_SCONF|awk '{print $3}'`

Patch0:    0001-coreutils-8.31-i18n.patch
Patch1:    0001-disable-test-of-rwlock.patch
# uname -p/-i to display processor type
Patch2:    coreutils-8.2-uname-processortype.patch
# df --direct
Patch3:    coreutils-df-direct.patch

Patch4:    coreutils-getgrouplist.patch
Patch5:    bugfix-remove-usr-local-lib-from-m4.patch
Patch6:    bugfix-dummy_help2man.patch
Patch7:    bugfix-selinux-flask.patch
Patch8:    skip-the-tests-that-require-selinux-if-selinux-is-di.patch 

Patch9:    coreutils-8.32-ls-removed-dir.patch
Patch10:   coreutils-8.32-leaf-opt-xfs.patch
Patch6000: 2bc66c5ea7e507786a45c1b6b15fe74a338240f4.patch

Conflicts: filesystem < 3
# To avoid clobbering installs
Provides: /bin/sh

Conflicts: %{name}-single
Obsoletes: %{name}-common < %{version}-%{release}
Provides: %{name}-common = %{version}-%{release}

BuildRequires: attr, autoconf, automake, gcc, hostname, strace, texinfo
BuildRequires: gettext-devel, gmp-devel, libacl-devel, libattr-devel gdb
BuildRequires: libcap-devel, libselinux-devel, libselinux-utils, openssl-devel

Requires: ncurses, gmp
Requires(preun): /sbin/install-info
Requires(post): /sbin/install-info

Provides: coreutils-full = %{version}-%{release}
Provides: fileutils = %{version}-%{release}
Provides: mktemp = 4:%{version}-%{release}
Provides: sh-utils = %{version}-%{release}
Provides: stat = %{version}-%{release}
Provides: textutils = %{version}-%{release}
Obsoletes: %{name} < 8.24
Provides: bundled(gnulib)
Provides: /bin/basename, /bin/cat, /bin/chgrp, /bin/chmod, /bin/chown
Provides: /bin/cp, /bin/cut, /bin/date, /bin/dd, /bin/df, /bin/echo
Provides: /bin/env, /bin/false, /bin/ln, /bin/ls, /bin/mkdir, /bin/mknod
Provides: /bin/mktemp, /bin/mv, /bin/nice, /bin/pwd, /bin/readlink
Provides: /bin/rm, /bin/rmdir, /bin/sleep, /bin/sort, /bin/stty
Provides: /bin/sync, /bin/touch, /bin/true, /bin/uname

%description
These are the GNU core utilities.  This package is the combination of
the old GNU fileutils, sh-utils, and textutils packages.

%prep
%autosetup -N

%autopatch -p1

(echo ">>> Fixing permissions on tests") 2>/dev/null
find tests -name '*.sh' -perm 0644 -print -exec chmod 0755 '{}' '+'
(echo "<<< done") 2>/dev/null

autoreconf -fiv

%build
if [ %user = root ]; then
    export FORCE_UNSAFE_CONFIGURE=1
fi
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -fpic"
%{expand:%%global optflags %{optflags} -D_GNU_SOURCE=1}
mkdir separate && \
  (cd separate && ln -s ../configure || exit 1
%configure --with-openssl \
             --cache-file=../config.cache \
             --enable-install-program=arch \
             --enable-no-install-program=kill,uptime \
             --with-tty-group \
             DEFAULT_POSIX2_VERSION=200112 alternative=199209 || :
make all %{?_smp_mflags}

# make sure that parse-datetime.{c,y} ends up in debuginfo (#1555079)
ln -v ../lib/parse-datetime.{c,y} .
 )

%install
(cd separate && make DESTDIR=$RPM_BUILD_ROOT install)

# chroot was in /usr/sbin :
mkdir -p $RPM_BUILD_ROOT/{%{_bindir},%{_sbindir}}
mv $RPM_BUILD_ROOT/{%_bindir,%_sbindir}/chroot

%find_lang %name
# Add the %%lang(xyz) ownership for the LC_TIME dirs as well...
grep LC_TIME %name.lang | cut -d'/' -f1-6 | sed -e 's/) /) %%dir /g' >>%name.lang

%check
pushd separate
make check VERBOSE=yes
popd

%preun 
if [ $1 = 0 ]; then
  if [ -f %{_infodir}/%{name}.info.gz ]; then
    /sbin/install-info --delete %{_infodir}/%{name}.info.gz %{_infodir}/dir || :
  fi
fi

%post 
if [ -f %{_infodir}/%{name}.info.gz ]; then
  /sbin/install-info %{_infodir}/%{name}.info.gz %{_infodir}/dir || :
fi

%files -f %{name}.lang
%{_bindir}/*
%{_sbindir}/chroot
%dir %{_libexecdir}/coreutils
%{_libexecdir}/coreutils/*.so
%doc ABOUT-NLS NEWS README THANKS TODO
%license COPYING
%exclude %{_infodir}/dir

%package_help
%files help
%{_infodir}/coreutils*
%{_mandir}/man*/*

%changelog
* 20201117003007632079 patch-tracking 8.32-3
- append patch file of upstream repository from <2bc66c5ea7e507786a45c1b6b15fe74a338240f4> to <2bc66c5ea7e507786a45c1b6b15fe74a338240f4>

* Wed Aug 26 2020 chenbo pan <panchenbo@uniontech.com> - 8.32-2
- fix patch error

* Wed Jul 29 2020 Liquor <lirui130@hauwei.com> - 8.32-1
- update to 8.32

* Thu Apr 30 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.31-5
- Judge if selinux is enabled for the tests that requires selinux

* Sat Mar 14 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.31-4
- Add build requires of gdb

* Thu Feb 13 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.31-3
- Enable check and uname -p/-i as well as df --direct

* Fri Jan 10 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.31-2
- Strengthen patch

* Thu Jan 9 2020 openEuler Buildteam <buildteam@openeuler.org> - 8.31-1
- Update version to 8.31-1

* Wed Dec 25 2019 openEuler Buildteam <buildteam@openeuler.org> - 8.30-8
- Revert last commit

* Thu Dec 19 2019 openEuler Buildteam <buildteam@openeuler.org> - 8.30-7
- delete unneeded patch

* Wed Nov 6 2019 openEuler Buildteam <buildteam@openeuler.org> - 8.30-6
- delete unneeded comments

* Thu Aug 29 2019 hexiaowen <hexiaowen@huawei.com> - 8.30-5
- Package rebuild

* Wed Aug 21 2019 gaoyi <gaoyi15@huawei.com> - 8.30-4.h8
- Type: enhancement
- ID: NA
- SUG: NA
- DESC: remove patches' prefix starting with backport

* Wed May 08 2019 gulining<gulining1@huawei.com> - 8.30-4.h7
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:revert patch for rtos

* Wed May 8 2019 liusirui<liusirui@huawei.com> - 8.30-4.h6
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:rename some patches

* Sat Apr 6 2019 luochunsheng<luochunsheng@huawei.com> - 8.30-4.h5
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:remove sensitive information

* Fri Mar 15 2019 yanghua <yanghua21@huawei.com> - 8.30-4.h4
- Type:bugfix
- ID:NA
- SUG:restart
- DESC:echo always process escapes when POSIXLY_CORRECT is
       sync fix open fallback bug
       tail fix handling of broken pipes with SIGPIPE ignor
       seq output decimal points consistently with invalid

* Thu Feb 14 2019 zoujing <zoujing13@huawei.com> - 8.30-4.h3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:failed to exec scriptlet interpreter

* Wed Jan 23 2019 sunguoshuai <sunguoshuai@huawei.com> - 8.30-4.h2
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:sync 

* Fri Dec 28 2018 hushiyuan <hushiyuan@huawei.com> - 8.30-4.h1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:add provides to coreutils-single to make it a drop-in replacement (#1572693)
- reintroduce very old Provides (mktemp, sh-utils, textwrap, fileutils, stat)

* Thu Jul 12 2018 hexiaowen <hexiaowen@huawei.com> - 8.30-1
- Pacakge init