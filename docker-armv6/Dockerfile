FROM scratch
MAINTAINER Christopher Reimer
ADD archlinux-armv6h-latest.tar.gz /

RUN setarch armv6h /bin/sh -c "haveged -w 1024; pacman-key --init"
RUN setarch armv6h pacman-key --populate archlinuxarm
RUN setarch armv6h pacman -Rsc --noconfirm haveged
RUN setarch armv6h ln -s /usr/share/zoneinfo/UTC /etc/localtime
RUN setarch armv6h /bin/sh -c "echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen"
RUN setarch armv6h locale-gen

RUN setarch armv6h useradd -m -G wheel -s /bin/bash builduser
ADD builduser-pacman.sudoers /etc/sudoers.d/builduser-pacman

RUN setarch armv6h mkdir -p /builddir /pkgdest /srcdest /repo
RUN setarch armv6h chown -R builduser /builddir /pkgdest /srcdest /repo
RUN setarch armv6h /bin/sh -c "echo -e \"OPTIONS+=( 'debug')\nPKGDEST='/pkgdest'\nSRCDEST='/srcdest'\nBUILDDIR='/builddir'\nMAKEFLAGS='-j4'\nPACKAGER='repo-gen automatic build system'\n\" >> /etc/makepkg.conf"

