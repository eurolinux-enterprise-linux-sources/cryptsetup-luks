%define enable_fips 1
%define fipscheck_version 1.2.0
%define libgcrypt_version 1.4.5
%define device_mapper_version 1.02.61

Summary: A utility for setting up encrypted filesystems
Name: cryptsetup-luks
Version: 1.2.0
Release: 11%{?dist}
License: GPLv2
Group: Applications/System
URL: http://cryptsetup.googlecode.com/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: libgcrypt-devel >= %{libgcrypt_version}
BuildRequires: device-mapper-devel >= %{device_mapper_version}
BuildRequires: libgpg-error-devel, libuuid-devel, libsepol-devel
BuildRequires: libselinux-devel, popt-devel
%if %{enable_fips}
BuildRequires: fipscheck-devel >= %{fipscheck_version}
%endif
Provides: cryptsetup = %{version}-%{release}
Obsoletes: cryptsetup <= 0.1
Requires: cryptsetup-luks-libs = %{version}-%{release}

%define _root_sbindir /sbin
%define upstream_version %{version}
Source0: http://cryptsetup.googlecode.com/files/cryptsetup-%{upstream_version}.tar.bz2
Patch0: cryptsetup-crypto-backend.patch
Patch1: cryptsetup-fipscheck.patch
Patch2: cryptsetup-1.3.2-status.patch
Patch3: cryptsetup-1.3.3-fix-device-lookup.patch
Patch4: cryptsetup-1.4.1-fix-duplicate-status.patch

%description
This package contains cryptsetup, a utility for setting up
encrypted filesystems using Device Mapper and the dm-crypt target.

%package devel
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: libgcrypt-devel >= %{libgcrypt_version}
Requires: device-mapper-devel >= %{device_mapper_version}
Requires: pkgconfig, libuuid-devel
Summary: Headers and libraries for using encrypted filesystems

%description devel
The cryptsetup-luks-devel package contain libraries and header files
used for writing code that makes use of encrypted filesystems.

%package libs
Group: System Environment/Libraries
Summary: Cryptsetup shared library
Requires: device-mapper-libs >= %{device_mapper_version}

%description libs
This package contains the cryptsetup shared library, libcryptsetup.

%prep
%setup -q -n cryptsetup-%{upstream_version}
%patch0 -p1
%if %{enable_fips}
%patch1 -p1
%endif
%patch2 -p1
%patch3 -p1
%patch4 -p1

iconv -f latin1 -t utf8 ChangeLog > ChangeLog.new
mv -f ChangeLog.new ChangeLog 

%build
%configure  --sbindir=%{_root_sbindir} --libdir=/%{_lib}

# remove rpath
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

%if %{enable_fips}
# Generate HMAC checksums
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}} \
  %{__arch_install_post} \
  %{__os_install_post} \
  fipshmac $RPM_BUILD_ROOT/%{_lib}/libcryptsetup.so.*
%endif

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
rm -rf  $RPM_BUILD_ROOT/%{_lib}/*.la $RPM_BUILD_ROOT/%{_lib}/cryptsetup

# move libcryptsetup.so to %%{_libdir}
pushd $RPM_BUILD_ROOT/%{_lib}
rm libcryptsetup.so
mkdir -p $RPM_BUILD_ROOT/%{_libdir}
ln -s ../../%{_lib}/$(ls libcryptsetup.so.?.?.?) $RPM_BUILD_ROOT/%{_libdir}/libcryptsetup.so
mv $RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT/%{_libdir}
popd 
%find_lang cryptsetup

%post -n cryptsetup-luks-libs -p /sbin/ldconfig

%postun -n cryptsetup-luks-libs -p /sbin/ldconfig

%files -f cryptsetup.lang
%defattr(-,root,root,-)
%doc COPYING ChangeLog AUTHORS TODO FAQ
%{_mandir}/man8/cryptsetup.8.gz
%{_root_sbindir}/cryptsetup
%if %{enable_fips}
%endif

%files devel
%defattr(-,root,root,-)
%{_includedir}/libcryptsetup.h
%{_libdir}/libcryptsetup.so
%{_libdir}/pkgconfig/libcryptsetup.pc

%files libs
%defattr(-,root,root,-)
/%{_lib}/libcryptsetup.so.*
%if %{enable_fips}
/%{_lib}/.libcryptsetup.so.*.hmac
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Mon Jun 23 2014 Ondrej Kozina <okozina@redhat.com> - 1.2.0-11
- remove unused log routine
  Resolves: #1112276

* Fri Jun 20 2014 Ondrej Kozina <okozina@redhat.com> - 1.2.0-10
- Update library constructor to issue warning
  Resolves: #1009707

* Thu Oct 10 2013 Ondrej Kozina <okozina@redhat.com> - 1.2.0-9
- remove FIPS check from cryptsetup utility constructor (not required)
  Resolves: #1009707

* Fri Oct 04 2013 Ondrej Kozina <okozina@redhat.com> - 1.2.0-8
- Add constructors to library and cryptsetup utlitity for FIPS.
  Resolves: #1009707

* Wed Feb 29 2012 Milan Broz <mbroz@redhat.com> - 1.2.0-7
- Fix device lookup function.
- Fix duplicate directories displayed in status output.
  Resolves: #755478 #746648

* Mon Aug 29 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-6
- Fix return code for status command when device doesn't exists.
  Resolves: #732179

* Wed Jun 15 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-5
- Move informational FIPS mode message to verbose mode.
  Resolves: #713410

* Mon May 09 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-4
- Disable volume key access function in FIPS mode.
  Resolves: #701936

* Mon Apr 04 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-3
- Require updated device mapper library (secure flag).
- Use FIPS RNG for keyslot salt in FIPS mode.
  Resolves: #692512 #693371

* Mon Feb 07 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-2
- Require libgcrypt and device-mapper versions supporting FIPS extensions.
- Request buffer wipe for dm-ioctl when sending key data.
  Resolves: #674825

* Mon Jan 10 2011 Milan Broz <mbroz@redhat.com> - 1.2.0-1
- Update to cryptsetup 1.2.0
- Use generic crypto backend interface.
- Add fipscheck compile option.
- Use gcrypt RNG in FIPS mode for key generation.
- Add FAQ to documentation.
  Resolves: #658817 #663870 #663869

* Tue Aug 10 2010 Milan Broz <mbroz@redhat.com> - 1.1.2-2
- Use default 1MiB data alignment.
  Resolves: #621684

* Mon Jun 07 2010 Milan Broz <mbroz@redhat.com> - 1.1.2-1
- Fix handling of newline with keyfile on standard input.
- Fix alignment ioctl use.
- Fix API activation calls to handle NULL device name.
  Resolves: #598523 #569949 #599617

* Tue May 25 2010 Milan Broz <mbroz@redhat.com> - 1.1.1-1
- Update to cryptsetup 1.1.1
- Fix luksClose for stacked LUKS/LVM devices.
  Resolves: #593487

* Wed May 05 2010 Milan Broz <mbroz@redhat.com> - 1.1.1-0.2
- Update to cryptsetup 1.1.1-rc2.
- Align device using topology info if available.
  Resolves: #569949

* Sun Jan 17 2010 Milan Broz <mbroz@redhat.com> - 1.1.0-1
- Update to cryptsetup 1.1.0.

* Fri Jan 15 2010 Milan Broz <mbroz@redhat.com> - 1.1.0-0.6
- Update to cryptsetup 1.1.0-rc4
- Fix gcrypt initialisation.
- Fix backward compatibility for hash algorithm (uppercase).

* Mon Nov 16 2009 Milan Broz <mbroz@redhat.com> - 1.1.0-0.4
- Update to cryptsetup 1.1.0-rc3

* Thu Oct 01 2009 Milan Broz <mbroz@redhat.com> - 1.1.0-0.3
- Update to cryptsetup 1.1.0-rc2
- Fix libcryptsetup to properly export only versioned symbols.

* Tue Sep 29 2009 Milan Broz <mbroz@redhat.com> - 1.1.0-0.2
- Update to cryptsetup 1.1.0-rc1
- Add luksHeaderBackup and luksHeaderRestore commands.

* Thu Sep 11 2009 Milan Broz <mbroz@redhat.com> - 1.1.0-0.1
- Update to new upstream testing version with new API interface.
- Add luksSuspend and luksResume commands.
- Introduce pkgconfig.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Milan Broz <mbroz@redhat.com> - 1.0.7-1
- Update to upstream final release.
- Split libs subpackage.
- Remove rpath setting from cryptsetup binary.

* Wed Jul 15 2009 Till Maas <opensource@till.name> - 1.0.7-0.2
- update BR because of libuuid splitout from e2fsprogs

* Mon Jun 22 2009 Milan Broz <mbroz@redhat.com> - 1.0.7-0.1
- Update to new upstream 1.0.7-rc1.

- Wipe old fs headers to not confuse blkid (#468062)
* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.6-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 30 2008 Milan Broz <mbroz@redhat.com> - 1.0.6-6
- Wipe old fs headers to not confuse blkid (#468062)

* Tue Sep 23 2008 Milan Broz <mbroz@redhat.com> - 1.0.6-5
- Change new project home page.
- Print more descriptive messages for initialization errors.
- Refresh patches to versions commited upstream.

* Sat Sep 06 2008 Milan Broz <mbroz@redhat.com> - 1.0.6-4
- Fix close of zero decriptor.
- Fix udevsettle delays - use temporary crypt device remapping.

* Wed May 28 2008 Till Maas <opensource till name> - 1.0.6-3
- remove a duplicate sentence from the manpage (RH #448705)
- add patch metadata about upstream status

* Tue Apr 15 2008 Bill Nottinghm <notting@redhat.com> - 1.0.6-2
- Add the device to the luksOpen prompt (#433406)
- Use iconv, not recode (#442574)

* Thu Mar 13 2008 Till Maas <opensource till name> - 1.0.6-1
- Update to latest version
- remove patches that have been merged upstream

* Mon Mar 03 2008 Till Maas <opensource till name> - 1.0.6-0.1.pre2
- Update to new version with several bugfixes
- remove patches that have been merged upstream
- add patch from cryptsetup newsgroup
- fix typo / missing luksRemoveKey in manpage (patch)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.0.5-9
- Autorebuild for GCC 4.3

* Sat Jan 19 2008 Peter Jones <pjones@redhat.com> - 1.0.5-8
- Rebuild for broken deps.

* Thu Aug 30 2007 Till Maas <opensource till name> - 1.0.5-7
- update URL
- update license tag
- recode ChangeLog from latin1 to uf8
- add smp_mflags to make

* Fri Aug 24 2007 Till Maas <opensource till name> - 1.0.5-6
- cleanup BuildRequires:
- removed versions, packages in Fedora are new enough
- changed popt to popt-devel

* Thu Aug 23 2007 Till Maas <opensource till name> - 1.0.5-5
- fix devel subpackage requires
- remove empty NEWS README
- remove uneeded INSTALL
- remove uneeded ldconfig requires
- add readonly detection patch

* Wed Aug 08 2007 Till Maas <opensource till name> - 1.0.5-4
- disable patch2, libsepol is now detected by configure
- move libcryptsetup.so to %%{_libdir} instead of /%%{_lib}

* Fri Jul 27 2007 Till Maas <opensource till name> - 1.0.5-3
- Use /%%{_lib} instead of /lib to use /lib64 on 64bit archs

* Thu Jul 26 2007 Till Maas <opensource till name> - 1.0.5-2
- Use /lib as libdir (#243228)
- sync header and library (#215349)
- do not use %%makeinstall (recommended by PackageGuidelines)
- select sbindir with %%configure instead with make
- add TODO

* Wed Jun 13 2007 Jeremy Katz <katzj@redhat.com> - 1.0.5-1
- update to 1.0.5

* Mon Jun 04 2007 Peter Jones <pjones@redhat.com> - 1.0.3-5
- Don't build static any more.

* Mon Feb 05 2007 Alasdair Kergon <agk@redhat.com> - 1.0.3-4
- Add build dependency on new device-mapper-devel package.
- Add preun and post ldconfig requirements.
- Update BuildRoot.

* Wed Nov  1 2006 Peter Jones <pjones@redhat.com> - 1.0.3-3
- Require newer libselinux (#213414)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.0.3-2.1
- rebuild

* Wed Jun  7 2006 Jeremy Katz <katzj@redhat.com> - 1.0.3-2
- put shared libs in the right subpackages

* Fri Apr  7 2006 Bill Nottingham <notting@redhat.com> 1.0.3-1
- update to final 1.0.3

* Wed Feb 27 2006 Bill Nottingham <notting@redhat.com> 1.0.3-0.rc2
- update to 1.0.3rc2, fixes bug with HAL & encrypted devices (#182658)

* Wed Feb 22 2006 Bill Nottingham <notting@redhat.com> 1.0.3-0.rc1
- update to 1.0.3rc1, reverts changes to default encryption type

* Tue Feb 21 2006 Bill Nottingham <notting@redhat.com> 1.0.2-1
- update to 1.0.2, fix incompatiblity with old cryptsetup (#176726)

* Mon Feb 20 2006 Karsten Hopp <karsten@redhat.de> 1.0.1-5
- BuildRequires: libselinux-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.0.1-4.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.0.1-4.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Dec  5 2005 Bill Nottingham <notting@redhat.com> 1.0.1-4
- rebuild against new libdevmapper

* Thu Oct 13 2005 Florian La Roche <laroche@redhat.com>
- add -lsepol to rebuild on current fc5

* Mon Aug 22 2005 Karel Zak <kzak@redhat.com> 1.0.1-2
- fix cryptsetup help for isLuks action

* Fri Jul  1 2005 Bill Nottingham <notting@redhat.com> 1.0.1-1
- update to 1.0.1 - fixes incompatiblity with previous cryptsetup for
  piped passwords

* Thu Jun 16 2005 Bill Nottingham <notting@redhat.com> 1.0-2
- add patch for 32/64 bit compatibility (#160445, <redhat@paukstadt.de>)

* Tue Mar 29 2005 Bill Nottingham <notting@redhat.com> 1.0-1
- update to 1.0

* Thu Mar 10 2005 Bill Nottingham <notting@redhat.com> 0.993-1
- switch to cryptsetup-luks, for LUKS support

* Tue Oct 12 2004 Bill Nottingham <notting@redhat.com> 0.1-4
- oops, make that *everything* static (#129926)

* Tue Aug 31 2004 Bill Nottingham <notting@redhat.com> 0.1-3
- link some things static, move to /sbin (#129926)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Apr 16 2004 Bill Nottingham <notting@redhat.com> 0.1-1
- initial packaging
