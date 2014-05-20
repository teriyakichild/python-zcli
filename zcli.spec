%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define module_name zcli

Name:           python-%{module_name}
Version:        0.1.0
Release:        1
Summary:        Zabbix CLI.

License:        ASLv2
URL:            https://github.com/rackerlabs/zabbix-usersync
Source0:        %{module_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-setuptools


%description

%prep
%setup -q -n %{module_name}-%{version}


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT

%files
%doc README.md LICENSE.md CHANGELOG
%{python_sitelib}/*
%attr(0755,-,-) %{_bindir}/zcli

%changelog
* Tue May 20 2014 Tony Rogers <tony.rogers@rackspace.com> - 0.1.0
- Initial spec
