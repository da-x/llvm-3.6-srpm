%define _prefix /opt/llvm-5.0.1

Name:		libcxxabi-5.0.1
Version:	5.0.1
Release:	1.svn308470%{?dist}.alonid
Summary:	Low level support for a standard C++ library
License:	MIT or NCSA
URL:		http://libcxxabi.llvm.org/
Source0:	http://llvm.org/releases/%{version}/5df6b5da0deba63bbf9046bcaa385241c4d72847.tar.gz
BuildRequires:	clang-5.0.1 llvm-5.0.1-devel llvm-5.0.1-static
BuildRequires:	libcxx-5.0.1-devel >= %{version}
%if 0%{?rhel}
# libcxx-devel has this, so we need to as well.
ExcludeArch:	ppc64 ppc64le
%endif

%if 0%{?epel} == 6
BuildRequires:	cmake3
BuildRequires:	devtoolset-2-gcc
BuildRequires:	devtoolset-2-binutils
BuildRequires:	devtoolset-2-gcc-c++
BuildRequires:	devtoolset-2-gcc-plugin-devel
%else
BuildRequires:	cmake
%endif

%description
libcxxabi provides low level support for a standard C++ library.

%package devel
Summary:	Headers and libraries for libcxxabi devel
Requires:	%{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}.

%package static
Summary:	Static libraries for libcxxabi

%description static
%{summary}.

%prep
%setup -q -n libcxxabi-5df6b5da0deba63bbf9046bcaa385241c4d72847

sed -i 's|${LLVM_BINARY_DIR}/share/llvm/cmake|%{_libdir}/cmake/llvm|g' CMakeLists.txt

%build
%ifarch armv7hl
# disable ARM exception handling
sed -i 's|LIBCXXABI_ARM_EHABI 1|LIBCXXABI_ARM_EHABI 0|g' include/__cxxabi_config.h
%endif

mkdir _build
cd _build
%ifarch s390 s390x
%if 0%{?fedora} < 26
# clang requires z10 at minimum
# workaround until we change the defaults for Fedora
%global optflags %(echo %{optflags} | sed 's/-march=z9-109 /-march=z10 /')
%endif
%endif

%if 0%{?epel} == 6
source /opt/rh/devtoolset-2/enable
%endif

export LDFLAGS="-Wl,--build-id"
%if 0%{?epel} == 6
%cmake3 .. \
%else
%cmake .. \
%endif
	-DCMAKE_C_COMPILER=%{_bindir}/clang \
	-DCMAKE_CXX_COMPILER=%{_bindir}/clang++ \
	-DLLVM_CONFIG=%{_bindir}/llvm-config \
	-DCMAKE_CXX_FLAGS="-std=c++11" \
	-DLIBCXXABI_LIBCXX_INCLUDES=%{_includedir}/c++/v1/ \
%if 0%{?__isa_bits} == 64
	-DLIBCXXABI_LIBDIR_SUFFIX:STRING=64 \
%endif
	-DCMAKE_BUILD_TYPE=RelWithDebInfo


make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_includedir}
cd ..
cp -a include/* %{buildroot}%{_includedir}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license LICENSE.TXT
%doc CREDITS.TXT
%{_libdir}/libc++abi.so.*

%files devel
%{_includedir}/*.h
%{_libdir}/libc++abi.so

%files static
%{_libdir}/libc++abi.a

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

* Mon Feb 20 2017 Tom Callaway <spot@fedoraproject.org> - 3.9.0-1
- update to 3.9.0
- apply fixes from libcxx

* Wed Sep  7 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.1-1
- update to 3.8.1

* Mon Jul 25 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.0-2
- make static subpackage

* Tue May 3 2016 Tom Callaway <spot@fedoraproject.org> - 3.8.0-1
- initial package
