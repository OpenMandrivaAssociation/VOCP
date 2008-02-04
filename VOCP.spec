
# NOTE:
# This turned out to be a very messy software to 
# pack... it makes mr. lint crazy. I should remember
# to stay away from packaging GUI:s...
# 
# Should it live in /usr/local/? no...
# Should it live in /var/lib/? no...
# Should it live in /usr/lib/? no...
# Should I rewrite the whole software to please mr 
# lint? no way...
# 

%define name	VOCP
%define version	0.9.3
%define release	%mkrel 5

Summary:	The VOCP system is a complete voice messaging solution
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		System/Servers
URL:		http://www.vocpsystem.com/
Source0:	%{name}-%{version}.tar.bz2
Source1:	%{name}-%{version}-apache.conf.bz2
Source2:	vocplogo16x16.png
Source3:	vocplogo32x32.png
Source4:	vocplogo48x48.png
Requires(post,preun):	rpm-helper
Requires:	perl
Requires:	perl-Modem-Vgetty >= 0.04
Requires:	perl-XML-Mini >= 1.2.7
Requires:	perl-Audio-DSP >= 0.02-2mdk
Requires:	perl-MIME-tools
Requires:	perl-Tk
Requires:	mgetty-voice >= 1.1.30
Requires:	mgetty-contrib >= 1.1.30
Requires:	mgetty-sendfax >= 1.1.30
Requires:	mgetty-viewfax >= 1.1.30
Requires:	mgetty >= 1.1.30
Requires:	festival
BuildRequires:	perl-devel mgetty-voice >= 1.1.30
BuildRequires:	perl-XML-Mini >= 1.2.7
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The VOCP system is a complete voice messaging solution, featuring
voicemail boxes, email pagers and DTMF command shells.  Users can
navigate the system using a touch-tone phone, leave and retrieve
messages and execute programs on the host machine using the DTMF
command shells.

VOCP now features a graphical configuration utility, a message
retrieval, call center and faxing GUIs, as well as the core VOCP
voice messaging system and the VOCPweb web interface.  

%package	web
Summary:	VOCPweb - Part of the VOCP voice messaging system
Group:		System/Servers
Requires:	%{name} = %{version}
Requires:	perl-Crypt-CBC >= 2.08
Requires:	perl-Crypt-Blowfish
Requires:	perl-Crypt-Rijndael >= 0.05
Requires:	apache2

%description	web
The VOCP web interface, which permits users to retrieve voicemail
from anywhere through a browser!

The program, vocpweb.cgi, lets users view the number of messages
in the box, details (date and time) for each message and allows
users to download or even hear their messages with their browsers.

%prep

%setup -q -n vocp-%{version}

# fix strange perms
find . -type f | xargs chmod 644
find . -type d | xargs chmod 755

# path hacks instead of a patch
find . -type f | xargs %{__perl} -p -i -e "s|^#\!/usr/local/bin/perl|#\!/usr/bin/perl|g"
find . -type f | xargs %{__perl} -p -i -e "s|/usr/local/vocp/lib|%{_datadir}/vocp/lib|g"
find . -type f | xargs %{__perl} -p -i -e "s|/usr/local/vocp/|%{_datadir}/vocp/|g"
find . -type f | xargs %{__perl} -p -i -e "s|/usr/local/vocp|%{_datadir}/vocp|g"
find . -type f | xargs %{__perl} -p -i -e "s|/usr/local/bin|%{_bindir}|g"
find . -type f | xargs %{__perl} -p -i -e "s|/var/spool/voice/commands|%{_datadir}/vocp/voice/commands|g"

# fix the vocweb stuff
%{__perl} -p -i -e "s|\$Web_serv_user = \'nobody\'\;|\$Web_serv_user = \'apache\'\;|g" vocpweb/vocpweb.cgi
%{__perl} -p -i -e "s|^#cachedir.*|cachedir cache|g" prog/vocp.conf
%{__perl} -p -i -e "s|^#group.*|group vocp|g" prog/vocp.conf

%build

# build the perl stuff
pushd prog/VOCP
    %{__perl} Makefile.PL INSTALLDIRS=vendor PREFIX=%{_prefix} </dev/null
    %{__make}
    %{__make} test
popd

# build binaries
gcc %{optflags} -o prog/bin/pwcheck prog/bin/pwcheck.c
gcc %{optflags} -o prog/bin/xfer_to_vocp prog/bin/xfer_to_vocp.c

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

# install the perl stuff
pushd prog/VOCP
    %{__make} PREFIX=%{buildroot}/%{_prefix} install
popd

# make some directories
install -d %{buildroot}/var/spool/voice/messages/{num,day,system,menu}
install -d %{buildroot}/var/spool/voice/messages/incoming/cache
install -d %{buildroot}/%{_sysconfdir}/vocp
install -d %{buildroot}/%{_sysconfdir}/logrotate.d
install -d %{buildroot}/%{_datadir}/vocp/{bin,lib,run}
install -d %{buildroot}/%{_datadir}/vocp/voice/commands
install -d %{buildroot}/%{_sysconfdir}/httpd/conf.d
install -d %{buildroot}/%{_liconsdir}
install -d %{buildroot}/%{_iconsdir}
install -d %{buildroot}/%{_miconsdir}
install -d %{buildroot}/%{_bindir}

mv prog/VOCP/Changes Changes.VOCP
mv doc/README doc/README.docs
mv prog/bin/README prog/README.bin

mv vocpweb/INSTALL INSTALL.vocpweb
mv vocpweb/README README.vocpweb
mv vocpweb/SECURITY SECURITY.vocpweb

# install config files
install -m644 prog/boxes.conf %{buildroot}/%{_sysconfdir}/vocp/
install -m644 prog/boxes.conf.sample %{buildroot}/%{_sysconfdir}/vocp/
install -m640 prog/boxes.conf.shadow %{buildroot}/%{_sysconfdir}/vocp/
install -m644 prog/cid-filter.conf %{buildroot}/%{_sysconfdir}/vocp/
install -m644 prog/vocp.conf %{buildroot}/%{_sysconfdir}/vocp/

# install commands
install -m755 commands/* %{buildroot}/%{_datadir}/vocp/voice/commands/

# install images
cp -aRf images %{buildroot}/%{_datadir}/vocp/

# install messages
cp -aRf messages %{buildroot}/%{_datadir}/vocp/

# install sounds
cp -aRf sounds %{buildroot}/%{_datadir}/vocp/

# install lib
install -m644 prog/lib/* %{buildroot}/%{_datadir}/vocp/lib/

# install binaries and other perl stuff
install -m755 modify_sample_rate.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/boxconf.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/callcenter.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/cnd-logger.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/convert_boxconf.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/convert_fax.sh %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/cryptpass.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/debug/beeveegetty.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/email2vm.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/pvftomp3 %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/pvftoogg %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/toggleEmail2Vm.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/txttopvf %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/view_fax.sh %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/vocphax.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/vocplocal.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/wav2rmd.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/bin/xvocp.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m755 prog/vocp.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m2755 prog/bin/messages.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m2755 prog/bin/pwcheck %{buildroot}/%{_datadir}/vocp/bin/
install -m2755 prog/bin/pwcheck.pl %{buildroot}/%{_datadir}/vocp/bin/
install -m4755 prog/bin/xfer_to_vocp %{buildroot}/%{_datadir}/vocp/bin/
install -m4755 prog/bin/xfer_to_vocp.pl %{buildroot}/%{_datadir}/vocp/bin/

# install vocpweb
cp -aRf vocpweb %{buildroot}/%{_datadir}/vocp/
bzcat %{SOURCE1} > %{buildroot}/%{_sysconfdir}/httpd/conf.d/a10_vocpweb.conf
chmod 640 %{buildroot}/%{_sysconfdir}/httpd/conf.d/a10_vocpweb.conf

# fix the doc dir (for help files)
ln -s ../doc/%{name}-%{version} %{buildroot}/%{_datadir}/vocp/doc

# fix softlinks for some of the executables
ln -s %{_datadir}/vocp/bin/xvocp.pl %{buildroot}/%{_bindir}/xvocp
ln -s %{_datadir}/vocp/bin/boxconf.pl %{buildroot}/%{_bindir}/boxconf
ln -s %{_datadir}/vocp/bin/callcenter.pl %{buildroot}/%{_bindir}/callcenter
ln -s %{_datadir}/vocp/bin/vocphax.pl %{buildroot}/%{_bindir}/vocphax

# fix menu stuff


mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-xvocp.desktop << EOF
[Desktop Entry]
Name=VOCP (VOCP Graphical voice message retrieval)
Comment=Xvocp presents a graphical user interface to the contents of voice mail boxes
Exec=%{_bindir}/xvocp
Icon=vocp
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Communications;
EOF

cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-boxconf.desktop << EOF
[Desktop Entry]
Name=Boxconf (VOCP Box Configuration interface)
Comment=Boxconf presents a graphical user interface used to administer the VOCP system box configuration
Exec=%{_bindir}/boxconf
Icon=vocp
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Communications;
EOF

cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-callcenter.desktop << EOF
[Desktop Entry]
Name=Callcenter (VOCP Call Center)
Comment=The VOCP call center is meant to be an "always on" call monitor and to give quick access to other VOCP GUIs and your call log
Exec=%{_bindir}/callcenter
Icon=vocp
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Communications;
EOF

cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-vocphax.desktop << EOF
[Desktop Entry]
Name=VOCPhax (VOCP Fax Viewer and Sender GUI)
Comment=VOCPhax presents a (hopefully) friendly and intuitive graphical interface to view and send faxes
Exec=%{_bindir}/vocphax
Icon=vocp
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Communications;
EOF

# install script to call the web interface from the menu.
cat > %{buildroot}/%{_datadir}/vocp/bin/%{name}-web << EOF
#!/bin/sh
url='http://localhost/vocpweb/index.html'
if ! [ -z "\$BROWSER" ] && ( which \$BROWSER ); then
  browser=\`which \$BROWSER\`
elif [ -x /usr/bin/netscape ]; then
  browser=/usr/bin/netscape
elif [ -x /usr/bin/konqueror ]; then
  browser=/usr/bin/konqueror
elif [ -x /usr/bin/lynx ]; then
  browser='xterm -bg black -fg white -e lynx'
elif [ -x /usr/bin/links ]; then
  browser='xterm -bg black -fg white -e links'
else
  xmessage "No web browser found, install one or set the BROWSER environment variable!"
  exit 1
fi
\$browser \$url
EOF
chmod 755 %{buildroot}/%{_datadir}/vocp/bin/%{name}-web

# install menu entry.

mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications
cat > $RPM_BUILD_ROOT%{_datadir}/applications/mandriva-%{name}-web.desktop << EOF
[Desktop Entry]
Name=VOCPweb (VOCP Web Remote Message Retrieval)
Comment=VOCPweb allows you to log on to the VOCP voice messaging system and retrieve messages through a browser
Exec=%{_datadir}/vocp/bin/%{name}-web 1>/dev/null 2>/dev/null
Icon=vocp
Terminal=false
Type=Application
Categories=X-MandrivaLinux-MoreApplications-Communications;
EOF


install -m644 %{SOURCE2} %{buildroot}/%{_miconsdir}/vocp.png
install -m644 %{SOURCE3} %{buildroot}/%{_iconsdir}/vocp.png
install -m644 %{SOURCE4} %{buildroot}/%{_liconsdir}/vocp.png

# fix logrotate stuff
cat > %{buildroot}/%{_sysconfdir}/logrotate.d/callcenter << EOF
/var/log/vocp-calls.log {
    create 0644 root vocp
    rotate 4
    missingok
    nocompress
}
EOF
chmod 644 %{buildroot}/%{_sysconfdir}/logrotate.d/callcenter

%pre
%_pre_useradd vocp /var/spool/voice /bin/true

%post
%update_menus

%postun
%_postun_userdel vocp
%clean_menus

%post		web
%update_menus

%postun		web
%clean_menus

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-, root, root)
%doc Changes.VOCP doc/* CHANGELOG INSTALL README prog/README.bin
%attr(0755,root,vocp) %dir %{_sysconfdir}/vocp
%attr(0644,root,vocp) %config(noreplace) %{_sysconfdir}/vocp/boxes.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/vocp/boxes.conf.sample
%attr(0640,root,vocp) %config(noreplace) %{_sysconfdir}/vocp/boxes.conf.shadow
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/vocp/cid-filter.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/vocp/vocp.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/callcenter
%dir %{_datadir}/vocp
%dir %{_datadir}/vocp/voice
%dir %{_datadir}/vocp/voice/commands
%attr(0755,root,root) %{_datadir}/vocp/voice/commands/date.pl
%attr(0755,root,root) %{_datadir}/vocp/voice/commands/echo.pl
%attr(0755,root,root) %{_datadir}/vocp/voice/commands/ip.pl
%attr(0755,root,root) %{_datadir}/vocp/voice/commands/motd.pl
%attr(0755,root,root) %{_datadir}/vocp/voice/commands/seleclisting.pl
%{_datadir}/vocp/images
%{_datadir}/vocp/messages
%{_datadir}/vocp/sounds
%{_datadir}/vocp/lib
%dir %{_datadir}/vocp/bin
%attr(0755,root,root) %{_datadir}/vocp/bin/beeveegetty.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/boxconf.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/callcenter.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/cnd-logger.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/convert_boxconf.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/convert_fax.sh
%attr(0755,root,root) %{_datadir}/vocp/bin/cryptpass.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/email2vm.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/modify_sample_rate.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/pvftomp3
%attr(0755,root,root) %{_datadir}/vocp/bin/pvftoogg
%attr(0755,root,root) %{_datadir}/vocp/bin/toggleEmail2Vm.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/txttopvf
%attr(0755,root,root) %{_datadir}/vocp/bin/view_fax.sh
%attr(0755,root,root) %{_datadir}/vocp/bin/vocphax.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/vocplocal.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/vocp.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/wav2rmd.pl
%attr(0755,root,root) %{_datadir}/vocp/bin/xvocp.pl
%attr(2755,root,vocp) %{_datadir}/vocp/bin/messages.pl
%attr(2755,root,vocp) %{_datadir}/vocp/bin/pwcheck
%attr(2755,root,vocp) %{_datadir}/vocp/bin/pwcheck.pl
%attr(4755,root,vocp) %{_datadir}/vocp/bin/xfer_to_vocp
%attr(4755,root,vocp) %{_datadir}/vocp/bin/xfer_to_vocp.pl
%dir %attr(0755,root,root) %{_datadir}/vocp/run
%dir %attr(0755,root,root) %{_datadir}/vocp/doc
%dir %attr(0755,root,root) /var/spool/voice/messages/num
%dir %attr(0755,root,root) /var/spool/voice/messages/day
%dir %attr(0755,root,root) /var/spool/voice/messages/system
%dir %attr(0755,root,root) /var/spool/voice/messages/menu
%dir %attr(1777,root,vocp) /var/spool/voice/messages/incoming
%dir %attr(1777,root,vocp) /var/spool/voice/messages/incoming/cache
%{perl_vendorlib}/*.pm
%{perl_vendorlib}/VOCP
%{perl_vendorlib}/auto/VOCP
%{_mandir}/man3*/*
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) %{_datadir}/applications/mandriva-xvocp.desktop
%attr(0644,root,root) %{_datadir}/applications/mandriva-boxconf.desktop
%attr(0644,root,root) %{_datadir}/applications/mandriva-callcenter.desktop
%attr(0644,root,root) %{_datadir}/applications/mandriva-vocphax.desktop
%attr(0644,root,root) %{_miconsdir}/*.png
%attr(0644,root,root) %{_iconsdir}/*.png
%attr(0644,root,root) %{_liconsdir}/*.png

%files web
%defattr(-, root, root)
%doc INSTALL.vocpweb README.vocpweb SECURITY.vocpweb
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/httpd/conf.d/a10_vocpweb.conf
%dir %{_datadir}/vocp/vocpweb
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/index.html
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/styles.css
%attr(0755,root,root) %{_datadir}/vocp/vocpweb/vocpweb.cgi
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/vocpwebhelp.html
%dir %{_datadir}/vocp/vocpweb/img
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/img/*.gif
%dir %{_datadir}/vocp/vocpweb/tpl
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/tpl/*.html
%dir %attr(1777,root,vocp) %{_datadir}/vocp/vocpweb/sounds
%attr(0644,root,root) %{_datadir}/vocp/vocpweb/sounds/index.html
%attr(0755,root,root) %{_datadir}/vocp/bin/%{name}-web
%attr(0644,root,root)%{_datadir}/applications/mandriva-%{name}-web.desktop

