Summary:        RADIUS proxy that also supports TLS (RadSec)
Name:           radsecproxy
Version:        1.6.7
Release:        2tiri%{?dist}
Autoreqprov:    on
Group:          Productivity/Networking/Radius/Clients
License:        GPL-2+
URL:            http://software.uninett.no/radsecproxy/
Source0:        %{name}-%{version}.tar.xz
Source1:        %{name}.init
Source2:        %{name}-rpmlintrc
Source3:        %{name}-stats.sh
Source100:      %{name}.service
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  openssl-devel patch nettle-devel
%if "%{?dist}" == ".el7"
BuildRequires:  systemd
%{?systemd_requires}
%endif

#### FIXME #### systemd!!!

%description
radsecproxy is a generic RADIUS proxy that in addition to to usual RADIUS UDP
transport, also supports TLS (RadSec). The aim is for the proxy to have
sufficient features to be flexible, while at the same time to be small,
efficient and easy to configure.

%prep
%setup -n %{name}-%{version}
#%patch1 -p1

%build
# set DOCBOOK2X_MAN to get extra man page
%configure --enable-fticks --sysconfdir=/etc
make %{?_smp_mflags}

%install
# copy and symlink the SysV init script:
mkdir -p %{buildroot}/%{_initddir}
install -D -m 755 %{SOURCE1} %{buildroot}/%{_initddir}/radsecproxy
mkdir -p %{buildroot}/%{_sbindir}
ln -sf %{_initrddir}/radsecproxy %{buildroot}%{_sbindir}/rcradsecproxy
# copy new config file
mkdir -p %{buildroot}/etc
install -D -m 640 radsecproxy.conf-example %{buildroot}/etc/radsecproxy.conf
# copy scripts
mkdir -p %{buildroot}/%{_bindir}
install -D -m 755 tools/naptr-eduroam.sh %{buildroot}/%{_bindir}
install -D -m 755 tools/radsec-dynsrv.sh %{buildroot}/%{_bindir}
install -D -m 755 %{SOURCE3} %{buildroot}/%{_bindir}/radsecproxy-stats.sh
# logfile as ghost file
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/
touch $RPM_BUILD_ROOT%{_localstatedir}/log/radsecproxy.log

# install systemd service 
install -D -m 755 %{SOURCE100} $RPM_BUILD_ROOT/%{_unitdir}/radsecproxy.service


%makeinstall

%post
%systemd_post radsecproxy.service
if [ $1 -eq 1 ]; then           # install
  # Initial installation
  # 2012-05-16 only on update inform the admin:
  if [ $1 -eq 2 ]
  then
        echo "-----------------------------------------------"
        echo "Please note that the default secret has changed"
        echo "in version 1.6 from \"mysecret\" to \"radsec\"!"
        echo "Please, check your configuration!"
        echo "(RADSECPROXY-19 / draft-ietf-radext-radsec-08)"
        echo "-----------------------------------------------"
  fi
fi
exit 0

%preun
%systemd_preun radsecproxy.service

%postun
%systemd_postun_with_restart radsecproxy.service

/bin/systemctl try-restart radsecproxy.service >/dev/null 2>&1 || :

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc COPYING NEWS AUTHORS ChangeLog LICENSE THANKS radsecproxy.conf-example
%config(noreplace) %{_sysconfdir}/radsecproxy.conf
%{_sbindir}/radsecproxy
%{_bindir}/radsecproxy-conf
%{_bindir}/radsecproxy-hash
%doc %{_mandir}/man1/*
%doc %{_mandir}/man5/*
%{_initddir}/radsecproxy
%{_sbindir}/rcradsecproxy
%{_bindir}/radsec-dynsrv.sh
%{_bindir}/naptr-eduroam.sh
%{_bindir}/radsecproxy-stats.sh
%ghost %{_localstatedir}/log/radsecproxy.log
%if "%{?dist}" == ".el7"
%{_unitdir}/radsecproxy.service
%endif

%changelog
* Tue Jul  5 2016 tom@tiri.li - 1.6.7-2tiri
- first setup for Red Hat Enterprise Linux 7
