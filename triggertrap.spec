%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

# XXX Need to add runtime dependencies
Name: triggertrap
Version: 0.1.0
Release: 1%{?dist}
Summary: TriggerTrap Extension for Arista EOS

Group: Development/Libraries
License: BSD (3-clause)
URL: http://www.arista.com
Source0: %{name}-%{version}.tar.gz

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Triggertrap Extension for EOS is an extension that monitors interface counters and generates an SNMP trap when a threshold is crossed.

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
%{python_sitelib}/triggertrap*
%{_bindir}/triggertrap
#/usr/triggertrap.conf
/persist/sys/triggertrap.conf
