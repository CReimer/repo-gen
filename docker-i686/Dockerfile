FROM scratch
MAINTAINER Christopher Reimer
ADD archlinux-i686-latest.tar.gz /

RUN setarch i686 /bin/sh -c "haveged -w 1024; pacman-key --init"
RUN setarch i686 pacman-key --populate archlinux
RUN setarch i686 pacman -Rsc --noconfirm haveged
RUN setarch i686 ln -s /usr/share/zoneinfo/UTC /etc/localtime
RUN setarch i686 /bin/sh -c "echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen"
RUN setarch i686 locale-gen

RUN setarch i686 useradd -m -G wheel -s /bin/bash builduser
ADD builduser-pacman.sudoers /etc/sudoers.d/builduser-pacman

RUN setarch i686 mkdir -p /builddir /pkgdest /srcdest /repo
RUN setarch i686 chown -R builduser /builddir /pkgdest /srcdest /repo
RUN setarch i686 /bin/sh -c "echo -e \"OPTIONS+=( 'debug')\nPKGDEST='/pkgdest'\nSRCDEST='/srcdest'\nBUILDDIR='/builddir'\nMAKEFLAGS='-j4'\nPACKAGER='repo-gen automatic build system'\n\" >> /etc/makepkg.conf"

