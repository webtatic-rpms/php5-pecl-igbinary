%{!?__pecl: %{expand: %%global __pecl %{_bindir}/pecl}}

%global    basepkg   php54w
%global    extname   igbinary

Summary:        Replacement for the standard PHP serializer
Name:           %{basepkg}-pecl-igbinary
Version:        1.2.1
Release:        1%{?dist}
License:        BSD
Group:          System Environment/Libraries

URL:            http://pecl.php.net/package/igbinary
Source0:        http://pecl.php.net/get/%{extname}-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildRequires:  %{basepkg}-devel >= 5.2.0
BuildRequires:  %{basepkg}-pecl-apcu-devel >= 3.1.7

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}
Provides:       php-pecl(%{extname}) = %{version}
Provides:       php-pecl-igbinary = %{version}
Provides:       php-pecl-igbinary = %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif

%description
Igbinary is a drop in replacement for the standard PHP serializer.

Instead of time and space consuming textual representation, 
igbinary stores PHP data structures in a compact binary form. 
Savings are significant when using memcached or similar memory
based storages for serialized data.


%package devel
Summary:       Igbinary developer files (header)
Group:         Development/Libraries
Requires:      php-pecl-%{extname}%{?_isa} = %{version}-%{release}
Requires:      php-devel

%description devel
These are the files needed to compile programs using Igbinary


%prep
%setup -q -c

cat <<EOF | tee %{extname}.ini
; Enable %{extname} extension module
extension=%{extname}.so

; Enable or disable compacting of duplicate strings
; The default is On.
;igbinary.compact_strings=On

; Use igbinary as session serializer
;session.serialize_handler=igbinary

; Use igbinary as APC serializer
;apc.serializer=igbinary
EOF

%build
cd %{extname}-%{version}
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
rm -rf %{buildroot}

make install -C %{extname}-%{version} \
     INSTALL_ROOT=%{buildroot}

install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%{__mkdir_p} %{buildroot}%{php_inidir}
install -D -m 644 %{extname}.ini %{buildroot}%{php_inidir}/%{extname}.ini


%check
cd %{extname}-%{version}

# simple module load test
# without APC to ensure than can run without
%{__php} --no-php-ini \
    --define extension_dir=modules \
    --define extension=%{extname}.so \
    --modules | grep %{extname}

# APC required for test 045
ln -s %{php_extdir}/apc.so modules/

NO_INTERACTION=1 make test | tee rpmtests.log
grep -q "FAILED TEST" rpmtests.log && exit 1


%clean
rm -rf %{buildroot}


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{extname} >/dev/null || :
fi


%files
%defattr(-,root,root,-)
%doc %{extname}-%{version}/COPYING
%doc %{extname}-%{version}/CREDITS
%doc %{extname}-%{version}/NEWS
%doc %{extname}-%{version}/README.md
%config(noreplace) %{php_inidir}/%{extname}.ini
%{php_extdir}/%{extname}.so
%{pecl_xmldir}/%{name}.xml


%files devel
%defattr(-,root,root,-)
%{php_incldir}/ext/%{extname}


%changelog
* Sat Sep 13 2014 Andy Thompson <andy@webtatic.com> - 1.2.1-1
- Import EPEL php-pecl-igbinary-1.1.1-3 RPM
- Remove obsolete withapc
- update to 1.2.1