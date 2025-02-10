#
# RPM Spec for Unibuild Package Builder
#
%define install_base        /usr/lib/perfsonar/
%define pslookup_base       %{install_base}/pslookup/
%define pslookup_bin_base   %{pslookup_base}/bin
%define pslookup_datadir    /var/lib/perfsonar/pslookup
%define command_base        %{pslookup_bin_base}/commands
%define template_base       %{pslookup_base}/templates
%define config_base         /etc/perfsonar/pslookup
%define doc_base            /usr/share/doc/perfsonar/pslookup
%define httpd_config_base   /etc/httpd/conf.d
%define publish_web_dir     /usr/lib/perfsonar/web-pslookup

#
# Python
#

# This is the version we like.
%define _python_version_major 3

%if 0%{?el7}
%error EL7 is no longer supported.  Try something newer.
%endif

%if 0%{?el8}%{?ol8}
# EL8 standardized on just the major version, as did EPEL.
%define _python python%{_python_version_major}

%else

# EL9+ has everyting as just plain python
%define _python python

%endif

#Version variables set by automated scripts
%define perfsonar_auto_version 1.0.0
%define perfsonar_auto_relnum 1

Name:		perfsonar-pslookup
Version:	%{perfsonar_auto_version}
Release:	%{perfsonar_auto_relnum}%{?dist}
Summary:	perfSONAR lookupServiceClient
BuildArch:	noarch
License:	ASL 2.0
Group:		Development/Libraries
URL:        http://www.perfsonar.net
Requires:       %{_python}-inotify
Requires:       %{_python}-urllib3
Requires:       %{_python}-requests
Requires:       %{_python}-jsonschema >= 3.0
BuildRequires:  %{_python}
BuildRequires:  %{_python}-setuptools
%{?systemd_requires: %systemd_requires}
BuildRequires: systemd

Source0:	perfsonar-pslookup-%{version}.tar.gz

%description
The perfSONAR lookup service client

%pre
/usr/sbin/groupadd -r perfsonar 2> /dev/null || :
/usr/sbin/useradd -g perfsonar -r -s /sbin/nologin -c "perfSONAR User" -d /tmp perfsonar 2> /dev/null || :

%prep
%setup -q -n perfsonar-pslookup-%{version}

%install
rm -rf %{buildroot}
make install PYTHON-ROOTPATH=%{buildroot} PERFSONAR-CONFIGPATH=%{buildroot}/%{config_base} PERFSONAR-ROOTPATH=%{buildroot}/%{pslookup_base} PERFSONAR-DATAPATH=%{buildroot}/%{pslookup_datadir} BINPATH=%{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_unitdir}/
install -m 644 systemd/* %{buildroot}/%{_unitdir}/

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)
%license LICENSE
%{config_base}/*
/usr/lib/perfsonar/pslookup/bin/pslookup_client_agent
/usr/lib/systemd/system/pslookup-service-client-agent.service

%post
mkdir -p /var/log/perfsonar
%systemd_post pslookup-service-client-agent.service
if [ "$1" = "1" ]; then
    systemctl enable --now pslookup-service-client-agent.service
fi
