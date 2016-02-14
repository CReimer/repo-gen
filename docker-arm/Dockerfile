FROM scratch
MAINTAINER Christopher Reimer
ADD archlinux-arm-latest.tar.gz /

RUN setarch arm /bin/sh -c "haveged -w 1024; pacman-key --init"
RUN setarch arm pacman-key --populate archlinuxarm
RUN setarch arm pacman -Rsc --noconfirm haveged
RUN setarch arm ln -s /usr/share/zoneinfo/UTC /etc/localtime
RUN setarch arm /bin/sh -c "echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen"
RUN setarch arm locale-gen

RUN setarch arm useradd -m -G wheel -s /bin/bash builduser
ADD builduser-pacman.sudoers /etc/sudoers.d/builduser-pacman

RUN setarch arm mkdir -p /builddir /pkgdest /srcdest /repo
RUN setarch arm chown -R builduser /builddir /pkgdest /srcdest /repo
RUN setarch arm /bin/sh -c "echo -e \"OPTIONS+=( 'debug')\nPKGDEST='/pkgdest'\nSRCDEST='/srcdest'\nBUILDDIR='/builddir'\nMAKEFLAGS='-j4'\nPACKAGER='repo-gen automatic build system'\n\" >> /etc/makepkg.conf"

