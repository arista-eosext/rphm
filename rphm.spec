%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

# XXX Need to add runtime dependencies
Name: rphm
Version: 1.0.0
Release: 1%{?dist}
Summary: Remote Port Health Manager (rphm) Extension for Arista EOS

Group: Development/Libraries
License: BSD (3-clause)
URL: http://www.arista.com
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Remote Port Health Manager (rphm) extension for EOS is an extension that monitors interface counters and generates an SNMP trap when a threshold is crossed.

%prep
%setup -q

%build
%{__python} setup.py build

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,eosadmin,-)
%{python_sitelib}/rphm*
%{_bindir}/rphm
#/usr/rphm.conf
/persist/sys/rphm.conf
