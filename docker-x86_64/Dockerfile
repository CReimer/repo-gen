FROM scratch
MAINTAINER Christopher Reimer
ADD archlinux-x86_64-latest.tar.gz /

RUN setarch x86_64 /bin/sh -c "haveged -w 1024; pacman-key --init"
RUN setarch x86_64 pacman-key --populate archlinux
RUN setarch x86_64 pacman -Rsc --noconfirm haveged
RUN setarch x86_64 ln -s /usr/share/zoneinfo/UTC /etc/localtime
RUN setarch x86_64 /bin/sh -c "echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen"
RUN setarch x86_64 locale-gen

RUN setarch x86_64 useradd -m -G wheel -s /bin/bash builduser
ADD builduser-pacman.sudoers /etc/sudoers.d/builduser-pacman

RUN setarch x86_64 mkdir -p /builddir /pkgdest /srcdest /repo
RUN setarch x86_64 chown -R builduser /builddir /pkgdest /srcdest /repo
RUN setarch x86_64 /bin/sh -c "echo -e \"OPTIONS+=( 'debug')\nPKGDEST='/pkgdest'\nSRCDEST='/srcdest'\nBUILDDIR='/builddir'\nMAKEFLAGS='-j4'\nPACKAGER='repo-gen automatic build system'\n\" >> /etc/makepkg.conf"

