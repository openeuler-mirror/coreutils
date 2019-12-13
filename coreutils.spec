Name:       coreutils
Version:    8.30
Release:    6
License:    GPLv3+
Summary:    A set of basic GNU tools commonly used in shell scripts
Url:        https://www.gnu.org/software/coreutils/
Source0:    https://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source50:   supported_utils
Source51:   coreutils-provides.inc
Source105:  coreutils-colorls.sh
Source106:  coreutils-colorls.csh

# do not make coreutils-single depend on /usr/bin/coreutils
%global __requires_exclude ^%{_bindir}/coreutils$

Patch1:   coreutils-8.30-renameatu.patch
Patch100: coreutils-8.26-test-lock.patch
Patch105: coreutils-8.26-selinuxenable.patch
Patch101: coreutils-6.10-manpages.patch
Patch102: coreutils-8.25-DIR_COLORS.patch
Patch103: coreutils-8.2-uname-processortype.patch
Patch104: coreutils-df-direct.patch
Patch107: coreutils-8.4-mkdir-modenote.patch
Patch703: sh-utils-2.0.11-dateman.patch
Patch713: coreutils-4.5.3-langinfo.patch
Patch800: coreutils-i18n.patch
Patch801: coreutils-i18n-expand-unexpand.patch
Patch804: coreutils-i18n-cut-old.patch
Patch803: coreutils-i18n-fix-unexpand.patch
Patch805: coreutils-i18n-fix2-expand-unexpand.patch
Patch806: coreutils-i18n-un-expand-BOM.patch
Patch807: coreutils-i18n-sort-human.patch
Patch808: coreutils-i18n-fold-newline.patch
Patch908: coreutils-getgrouplist.patch
Patch950: coreutils-selinux.patch

Patch6000: bugfix-remove-usr-local-lib-from-m4.patch
Patch6001: bugfix-dummy_help2man.patch
Patch6002: bugfix-selinux-flask.patch
Patch6003: echo-always-process-escapes-when-POSIXLY_CORRECT-is-.patch
Patch6004: sync-fix-open-fallback-bug.patch
Patch6005: tail-fix-handling-of-broken-pipes-with-SIGPIPE-ignor.patch
Patch6006: seq-output-decimal-points-consistently-with-invalid-.patch

Conflicts: filesystem < 3
# To avoid clobbering installs
Provides: /bin/sh

Conflicts: %{name}-single
Obsoletes: %{name}-common
Provides: %{name}-common = %{version}-%{release}

BuildRequires: attr, autoconf, automake, gcc, hostname, strace, texinfo
BuildRequires: gettext-devel, gmp-devel, libacl-devel, libattr-devel
BuildRequires: libcap-devel, libselinux-devel, libselinux-utils, openssl-devel

Requires: ncurses, gmp
Requires(preun): /sbin/install-info
Requires(post): /sbin/install-info

Provides: coreutils-full = %{version}-%{release}
%include %{SOURCE51}
Obsoletes: %{name} < 8.24

%description
These are the GNU core utilities.  This package is the combination of
the old GNU fileutils, sh-utils, and textutils packages.

%prep
%autosetup -N

tee DIR_COLORS{,.256color,.lightbgcolor} <src/dircolors.hin >/dev/null

%autopatch -p1

(echo ">>> Fixing permissions on tests") 2>/dev/null
find tests -name '*.sh' -perm 0644 -print -exec chmod 0755 '{}' '+'
(echo "<<< done") 2>/dev/null

autoreconf -fiv

%build
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

# Get the list of supported utilities
cp %SOURCE50 .

%install
(cd separate && make DESTDIR=$RPM_BUILD_ROOT install)

# chroot was in /usr/sbin :
mkdir -p $RPM_BUILD_ROOT/{%{_bindir},%{_sbindir}}
mv $RPM_BUILD_ROOT/{%_bindir,%_sbindir}/chroot

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
install -p -c -m644 DIR_COLORS{,.256color,.lightbgcolor} $RPM_BUILD_ROOT%{_sysconfdir}
install -p -c -m644 %SOURCE105 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/colorls.sh
install -p -c -m644 %SOURCE106 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/colorls.csh

%find_lang %name
# Add the %%lang(xyz) ownership for the LC_TIME dirs as well...
grep LC_TIME %name.lang | cut -d'/' -f1-6 | sed -e 's/) /) %%dir /g' >>%name.lang

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

%files -f supported_utils -f %{name}.lang
%dir %{_libexecdir}/coreutils
%{_libexecdir}/coreutils/*.so
%config(noreplace) %{_sysconfdir}/DIR_COLORS*
%config(noreplace) %{_sysconfdir}/profile.d/*
%doc ABOUT-NLS NEWS README THANKS TODO
%license COPYING
%exclude %{_infodir}/dir

%package_help
%files help
%{_infodir}/coreutils*
%{_mandir}/man*/*

%changelog
* Wed Nov 6 2019 shenyangyang <shenyangyang4@huawei.com> - 8.30-6
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
