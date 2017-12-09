%define _prefix /opt/llvm-5.0.1

# If you need to bootstrap this, turn this on.
# Otherwise, you have a loop with libcxxabi
%global bootstrap 1

Name:		libcxx-5.0.1
Version:	5.0.1
Release:	1.svn318837%{?dist}.alonid
Summary:	C++ standard library targeting C++11
License:	MIT or NCSA
URL:		http://libcxx.llvm.org/
Source0:	http://llvm.org/releases/%{version}/598ae4fa2e4da8b0a4b839c8c26b6cd3f672a968.tar.gz
BuildRequires:	clang-5.0.1 llvm-5.0.1-devel llvm-5.0.1-static
%if 0%{?epel} == 6
BuildRequires:	cmake3
%else
BuildRequires:	cmake
%endif
%if %{bootstrap} < 1
BuildRequires:	libcxxabi-5.0.1-devel
BuildRequires:	python3
%endif
# PPC64 (on EL7) doesn't like this code.
# /builddir/build/BUILD/libcxx-3.8.0.src/include/thread:431:73: error: '(9.223372036854775807e+18 / 1.0e+9)' is not a constant expression
# _LIBCPP_CONSTEXPR duration<long double> _Max = nanoseconds::max();
%if 0%{?rhel}
ExcludeArch:	ppc64 ppc64le
%endif

%description
libc++ is a new implementation of the C++ standard library, targeting C++11.

%package devel
Summary:	Headers and libraries for libcxx devel
Requires:	%{name}%{?_isa} = %{version}-%{release}
%if %{bootstrap} < 1
Requires:	libcxxabi-5.0.1-devel
%endif

%description devel
%{summary}.

%package static
Summary:	Static libraries for libcxx

%description static
%{summary}.

%prep
%setup -q -n libcxx-598ae4fa2e4da8b0a4b839c8c26b6cd3f672a968

%build
mkdir _build
cd _build
%ifarch s390 s390x
%if 0%{?fedora} < 26
# clang requires z10 at minimum
# workaround until we change the defaults for Fedora
%global optflags %(echo %{optflags} | sed 's/-march=z9-109 /-march=z10 /')
%endif
%endif
export LDFLAGS="-Wl,--build-id"
# Clang in older releases than f24 can't build this code without crashing.
# So, we use gcc there. But the really old version in RHEL 6 works. Huh.
%if 0%{?epel} == 6
%cmake3 .. \
%else
%cmake .. \
%endif
%if 0%{?rhel} == 6
	-DCMAKE_C_COMPILER=/opt/llvm-5.0.1/bin/clang \
	-DCMAKE_CXX_COMPILER=/opt/llvm-5.0.1/bin/clang++ \
%else
%if 0%{?fedora} >= 24
	-DCMAKE_C_COMPILER=/opt/llvm-5.0.1/bin/clang \
	-DCMAKE_CXX_COMPILER=/opt/llvm-5.0.1/bin/clang++ \
%else
	-DCMAKE_C_COMPILER=/usr/bin/gcc \
	-DCMAKE_CXX_COMPILER=/usr/bin/g++ \
%endif
%endif
	-DLLVM_CONFIG=%{_bindir}/llvm-config \
%if %{bootstrap} < 1
	-DLIBCXX_CXX_ABI=libcxxabi \
	-DLIBCXX_CXX_ABI_INCLUDE_PATHS=%{_includedir} \
	-DPYTHONINTERP_FOUND=ON \
	-DPYTHON_EXECUTABLE=%{_bindir}/python3 \
	-DLIBCXX_ENABLE_ABI_LINKER_SCRIPT=ON \
%endif
%if 0%{?__isa_bits} == 64
	-DLIBCXX_LIBDIR_SUFFIX:STRING=64 \
%endif
	-DCMAKE_BUILD_TYPE=RelWithDebInfo


make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSE.TXT
%doc CREDITS.TXT TODO.TXT
%{_libdir}/libc++.so.*

%files devel
%{_includedir}/c++/
%{_libdir}/libc++.so

%files static
%license LICENSE.TXT
%{_libdir}/libc++*.a


%changelog
* Fri Sep  8 2017 Tom Callaway <spot@fedoraproject.org> - 5.0.0-1
- update to 5.0.0

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 23 2017 Tom Callaway <spot@fedoraproject.org> - 4.0.1-1
- update to 4.0.1

* Sat Apr 22 2017 Tom Callaway <spot@fedoraproject.org> - 4.0.0-1
- update to 4.0.0

* Wed Mar  8 2017 Tom Callaway <spot@fedoraproject.org> - 3.9.1-1
- update to 3.9.1

* Fri Mar  3 2017 Tom Callaway <spot@fedoraproject.org> - 3.9.0-4
- LIBCXX_ENABLE_ABI_LINKER_SCRIPT=ON

* Wed Mar  1 2017 Tom Callaway <spot@fedoraproject.org> - 3.9.0-3
- disable bootstrap

* Tue Feb 21 2017 Dan Horák <dan[at]danny.cz> - 3.9.0-2
- apply s390(x) workaround only in Fedora < 26

* Mon Feb 20 2017 Tom Callaway <spot@fedoraproject.org> - 3.9.0-1
- update to 3.9.0 (match clang)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Aug 26 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.1-1
- update to 3.8.1

* Thu Jun 09 2016 Dan Horák <dan[at]danny.cz> - 3.8.0-4
- exclude Power only in EPEL
- default to z10 on s390(x)

* Thu May 19 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.0-3
- use gcc on el7, fedora < 24. use clang on el6 and f24+
  MAGIC.
- bootstrap on

* Tue May 3 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.0-2
- bootstrap off

* Tue May 3 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.0-1
- initial package
- bootstrap on
