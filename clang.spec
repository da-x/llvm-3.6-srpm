%define _prefix /opt/llvm-5.0.0

%define h_cfe 7e8743f82ac7957c66d9c2444996be5b1218673b
%define h_clang_tools_extra 58cffec4d74b21c1097de4298e637a31c637851a
%define h_test_suite 5a456733120cf04bd3700b3bfa6e8de2f970089b

%global clang_tools_binaries \
	%{_bindir}/clang-apply-replacements \
	%{_bindir}/clang-change-namespace \
	%{_bindir}/clang-include-fixer \
	%{_bindir}/clang-query \
	%{_bindir}/clang-reorder-fields \
	%{_bindir}/clang-rename \
	%{_bindir}/clang-tidy \
	%{_datadir}/clang/clang-include-fixer.py \
	%{_datadir}/clang/clang-tidy-diff.py \
	%{_datadir}/clang/run-clang-tidy.py \
	%{_datadir}/clang/run-find-all-symbols.py \
	%{_datadir}/clang/clang-include-fixer.el \
	%{_datadir}/clang/clang-rename.el \
	%{_datadir}/clang/clang-rename.py

%global clang_binaries \
	%{_bindir}/clang \
	%{_bindir}/clang++ \
	%{_bindir}/clang-5.0 \
	%{_bindir}/clang-check \
	%{_bindir}/clang-cl \
	%{_bindir}/clang-cpp \
	%{_bindir}/clang-format \
	%{_bindir}/clang-import-test \
	%{_bindir}/clang-offload-bundler

%global clang_format_tools \
	%{_datadir}/clang/clang-format-sublime.py \
	%{_datadir}/clang/clang-format.el \
	%{_datadir}/clang/clang-format.py \
	%{_datadir}/clang/clang-format-diff.py

%if 0%{?fedora}
%bcond_without python3
%else
%bcond_with python3
%endif

Name:		clang-5.0.0
Version:	5.0.0
Release:	5.svn312293%{?dist}.alonid
Summary:	A C language family front-end for LLVM

License:	NCSA
URL:		http://llvm.org

Source0:	http://llvm.org/releases/%{version}/cfe-%{h_cfe}.tar.gz
Source1:	http://llvm.org/releases/%{version}/clang-tools-extra-%{h_clang_tools_extra}.tar.gz
Source2:	http://llvm.org/releases/%{version}/test-suite-%{h_test_suite}.tar.gz

Source100:	clang-config.h

# This patch is required when the test suite is using python-lit 0.5.0.
Patch1:		0001-litsupport-Add-compatibility-cludge-so-it-still-work.patch
Patch2:		0001-docs-Fix-Sphinx-detection-with-out-of-tree-builds.patch
Patch3:		0001-test-Remove-FileCheck-not-count-dependencies.patch
Patch4:		0001-lit.cfg-Remove-substitutions-for-clang-llvm-tools.patch

%if 0%{?epel} == 6
BuildRequires:	cmake3
BuildRequires:	devtoolset-2-gcc
BuildRequires:	devtoolset-2-binutils
BuildRequires:	devtoolset-2-gcc-c++
BuildRequires:	devtoolset-2-gcc-plugin-devel
BuildRequires:	libffi-devel
BuildRequires:	python27
%else
BuildRequires:	cmake
%endif
BuildRequires:	llvm-%{version}-devel = %{version}
BuildRequires:	libxml2-devel
# llvm-static is required, because clang-tablegen needs libLLVMTableGen, which
# is not included in libLLVM.so.
BuildRequires:  llvm-%{version}-static = %{version}
BuildRequires:  perl-generators
BuildRequires:  ncurses-devel

# These build dependencies are required for the test suite.
%if 0%{?epel} != 6
%if %with python3
BuildRequires:  python3-lit
%else
BuildRequires:  python2-lit
%endif
%endif

BuildRequires: zlib-devel
BuildRequires: tcl
BuildRequires: python-virtualenv
%if 0%{?epel} == 6
BuildRequires:  libstdc++
BuildRequires:  libstdc++-devel
%else
BuildRequires:  libstdc++-static
%endif
%if 0%{?fedora}
BuildRequires: python3-sphinx
%endif

Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Patch100:         0001-Support-RPATH.patch

# clang requires gcc, clang++ requires libstdc++-devel
# - https://bugzilla.redhat.com/show_bug.cgi?id=1021645
# - https://bugzilla.redhat.com/show_bug.cgi?id=1158594
Requires:	libstdc++-devel
Requires:	gcc-c++


%description
clang: noun
    1. A loud, resonant, metallic sound.
    2. The strident call of a crane or goose.
    3. C-language family front-end toolkit.

The goal of the Clang project is to create a new C, C++, Objective C
and Objective C++ front-end for the LLVM compiler. Its tools are built
as libraries and designed to be loosely-coupled and extensible.

%package libs
Summary: Runtime library for clang
Requires: compiler-rt-%{version}%{?_isa} >= %{version}

%description libs
Runtime library for clang.

%package devel
Summary: Development header files for clang.
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development header files for clang.

%package analyzer
Summary:	A source code analysis framework
License:	NCSA and MIT
BuildArch:	noarch
Requires:	%{name} = %{version}-%{release}
# not picked up automatically since files are currently not installed in
# standard Python hierarchies yet
Requires:	python

%description analyzer
The Clang Static Analyzer consists of both a source code analysis
framework and a standalone tool that finds bugs in C and Objective-C
programs. The standalone tool is invoked from the command-line, and is
intended to run in tandem with a build of a project or code base.

%package tools-extra
Summary: Extra tools for clang
Requires: llvm-%{version}-libs%{?_isa} = %{version}
Requires: clang-%{version}-libs%{?_isa} = %{version}

%description tools-extra
A set of extra tools built using Clang's tooling API.

# Put git-clang-format in its own package, because it Requires git and python2
# and we don't want to force users to install all those dependenices if they
# just want clang.
%package -n git-clang-format-%{version}
Summary: clang-format integration for git
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: git
Requires: python2

%description -n git-clang-format-%{version}
clang-format integration for git.

%prep
%setup -T -q -b 1 -n clang-tools-extra-%{h_clang_tools_extra}
# %patch3 -p1 -b .lit-dep-fix

%setup -T -q -b 2 -n test-suite-%{h_test_suite}
# %patch1 -p1 -b .lit-fix

%setup -q -n cfe-%{h_cfe}
# %patch2 -p1 -b .docs-fix
%patch4 -p1 -b .lit-tools-fix
%patch100 -p1 -b .rpath


mv ../clang-tools-extra-%{h_clang_tools_extra} tools/extra

%build

%if 0%{?epel} == 6
if [[ "$LD_LIBRARY_PATH" == "" ]] ; then
    export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64
else
    export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64:$LD_LIBRARY_PATH
fi
export PATH=/opt/rh/python27/root/usr/bin:$PATH
if [[ "$PKG_CONFIG_PATH" == "" ]] ; then
    export PKG_CONFIG_PATH=/opt/rh/python27/root/usr/lib64/pkgconfig
else
    export PKG_CONFIG_PATH=/opt/rh/python27/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH
fi

source /opt/rh/devtoolset-2/enable
%endif

mkdir -p _build
cd _build
%if 0%{?epel} == 6
%cmake3 .. \
%else
%cmake .. \
%endif
	-DLLVM_LINK_LLVM_DYLIB:BOOL=ON \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG:FILEPATH=/opt/llvm-%{version}/bin/llvm-config-%{__isa_bits} \
	\
	-DCLANG_ENABLE_ARCMT:BOOL=ON \
	-DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON \
	-DCLANG_INCLUDE_DOCS:BOOL=ON \
	-DCLANG_INCLUDE_TESTS:BOOL=ON \
	-DCLANG_PLUGIN_SUPPORT:BOOL=ON \
	-DENABLE_LINKER_BUILD_ID:BOOL=ON \
	-DLLVM_ENABLE_EH=ON \
	-DLLVM_ENABLE_RTTI=ON \
	-DLLVM_BUILD_DOCS=ON \
%if 0%{?fedora}
	-DLLVM_ENABLE_SPHINX=ON \
%else
	-DLLVM_ENABLE_SPHINX=OFF \
%endif
	-DSPHINX_WARNINGS_AS_ERRORS=OFF \
	\
	-DCLANG_BUILD_EXAMPLES:BOOL=OFF \
%if 0%{?__isa_bits} == 64
        -DLLVM_LIBDIR_SUFFIX=64 \
%else
        -DLLVM_LIBDIR_SUFFIX= \
%endif
	-DLIB_SUFFIX=

make %{?_smp_mflags}

%install

%if 0%{?epel} == 6
if [[ "$LD_LIBRARY_PATH" == "" ]] ; then
    export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64
else
    export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64:$LD_LIBRARY_PATH
fi
export PATH=/opt/rh/python27/root/usr/bin:$PATH
if [[ "$PKG_CONFIG_PATH" == "" ]] ; then
    export PKG_CONFIG_PATH=/opt/rh/python27/root/usr/lib64/pkgconfig
else
    export PKG_CONFIG_PATH=/opt/rh/python27/root/usr/lib64/pkgconfig:$PKG_CONFIG_PATH
fi

source /opt/rh/devtoolset-2/enable
%endif

cd _build
make install DESTDIR=%{buildroot}

sed -i -e 's~#!/usr/bin/env python~#!/usr/bin/python2~' %{buildroot}%{_bindir}/git-clang-format

# multilib fix
mv -v %{buildroot}%{_includedir}/clang/Config/config{,-%{__isa_bits}}.h
install -m 0644 %{SOURCE100} %{buildroot}%{_includedir}/clang/Config/config.h

# bbedit (macOS-only editor) integration
rm -vf %{buildroot}%{_datadir}/clang/clang-format-bbedit.applescript

# TODO: Package html docs
rm -Rvf %{buildroot}%{_pkgdocdir}

%check

%if 0
# Needs fixing, error on EPEL7:
#
# lit: lit.cfg:200: note: using clang: '/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/_build/./bin/clang'
# lit: TestingConfig.py:115: fatal: unable to parse config file '/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/test/lit.cfg', traceback: Traceback (most recent call last):
#   File "/usr/lib/python2.7/site-packages/lit/TestingConfig.py", line 102, in load_from_path
#     exec(compile(data, path, 'exec'), cfg_globals, None)
#   File "/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/test/lit.cfg", line 490, in <module>
#     macOSSDKVersion = lit.util.findPlatformSdkVersionOnMacOS(config, lit_config)
# AttributeError: 'module' object has no attribute 'findPlatformSdkVersionOnMacOS'
# 
# make[3]: *** [test/CMakeFiles/check-clang] Error 2
# make[3]: Leaving directory `/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/_build'
# make[2]: *** [test/CMakeFiles/check-clang.dir/all] Error 2
# make[2]: Leaving directory `/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/_build'
# make[1]: *** [test/CMakeFiles/check-clang.dir/rule] Error 2
# make[1]: Leaving directory `/builddir/build/BUILD/cfe-7e8743f82ac7957c66d9c2444996be5b1218673b/_build'
# make: *** [check-clang] Error 2
# error: Bad exit status from /var/tmp/rpm-tmp.wMPabE (%check)
#     Bad exit status from /var/tmp/rpm-tmp.wMPabE (%check)
# 

# requires lit.py from LLVM utilities
cd _build
PATH=%{_libdir}/llvm:$PATH make check-clang

mkdir -p %{_builddir}/test-suite-%{version}.src/_build
cd %{_builddir}/test-suite-%{version}.src/_build

# FIXME: Using the cmake macro adds -Werror=format-security to the C/CXX flags,
# which causes the test suite to fail to build.
cmake .. -DCMAKE_C_COMPILER=%{buildroot}/usr/bin/clang \
         -DCMAKE_CXX_COMPILER=%{buildroot}/usr/bin/clang++
make %{?_smp_mflags} check || :
%endif

%files
%{_libdir}/clang/
%{clang_binaries}
%{clang_format_tools}
%{_bindir}/c-index-test
%if 0%{?fedora}
%{_mandir}/man1/clang.1
%endif
%{_datadir}/clang/bash-autocomplete.sh

%files libs
%{_libdir}/*.so.*
%{_libdir}/*.so

%files devel
%{_includedir}/clang/
%{_includedir}/clang-c/
%{_libdir}/cmake/*
%dir %{_datadir}/clang/
%if 0%{?fedora}
%{_datadir}/doc/clang/html/.buildinfo
%{_datadir}/doc/clang/html/*
%endif

%files analyzer
%{_bindir}/scan-view
%{_bindir}/scan-build
%{_libexecdir}/ccc-analyzer
%{_libexecdir}/c++-analyzer
%{_datadir}/scan-view/
%{_datadir}/scan-build/
%{_prefix}/share/man/man1/scan-build.1*

%files tools-extra
%{clang_tools_binaries}
%{_bindir}/find-all-symbols
%{_bindir}/modularize
%{_bindir}/clangd

%files -n git-clang-format-%{version}
%{_bindir}/git-clang-format

%changelog
* Wed Aug 30 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-5
- Add Requires: python for git-clang-format

* Sun Aug 06 2017 Björn Esser <besser82@fedoraproject.org> - 4.0.1-4
- Rebuilt for AutoReq cmake-filesystem

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release.

* Fri Jun 16 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-8
- Enable make check-clang

* Mon Jun 12 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-7
- Package git-clang-format

* Thu Jun 08 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-6
- Generate man pages

* Thu Jun 08 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-5
- Ignore test-suite failures until all arches are fixed.

* Mon Apr 03 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-4
- Run llvm test-suite

* Mon Mar 27 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-3
- Enable eh/rtti, which are required by lldb.

* Fri Mar 24 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-2
- Fix clang-tools-extra build
- Fix install

* Thu Mar 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- clang 4.0.0 final release

* Mon Mar 20 2017 David Goerger <david.goerger@yale.edu> - 3.9.1-3
- add clang-tools-extra rhbz#1328091

* Thu Mar 16 2017 Tom Stellard <tstellar@redhat.com> - 3.9.1-2
- Enable build-id by default rhbz#1432403

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com> - 3.9.1-1
- clang 3.9.1 final release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 14 2016 Nathaniel McCallum <npmccallum@redhat.com> - 3.9.0-3
- Add Requires: compiler-rt to clang-libs.
- Without this, compiling with certain CFLAGS breaks.

* Tue Nov  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 3.9.0-2
- Rebuild for new arches

* Fri Oct 14 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- clang 3.9.0 final release

* Fri Jul 01 2016 Stephan Bergmann <sbergman@redhat.com> - 3.8.0-2
- Resolves: rhbz#1282645 add GCC abi_tag support

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- clang 3.8.0 final release

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.4
- clang 3.8.0rc3

* Wed Feb 24 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.3
- package all libs into clang-libs.

* Wed Feb 24 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.2
- enable dynamic linking of clang against llvm

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- clang 3.8.0rc2

* Fri Feb 12 2016 Dave Airlie <airlied@redhat.com> 3.7.1-4
- rebuild against latest llvm packages
- add BuildRequires llvm-static

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 28 2016 Dave Airlie <airlied@redhat.com> 3.7.1-2
- just accept clang includes moving to /usr/lib64, upstream don't let much else happen

* Thu Jan 28 2016 Dave Airlie <airlied@redhat.com> 3.7.1-1
- initial build in Fedora.

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
