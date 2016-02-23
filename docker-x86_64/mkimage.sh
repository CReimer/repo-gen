#!/bin/bash

ARCH='x86_64'
DOCKER_IMAGE_NAME="archlinux-${ARCH}"
PACMAN_CONF="/usr/share/devtools/pacman-extra.conf"
TMP_CONF=/tmp/pacman.conf
sed "s/Architecture = auto/Architecture = ${ARCH}/" ${PACMAN_CONF} > ${TMP_CONF}

ROOTFS=$(mktemp -d ${TMPDIR:-/var/tmp}/rootfs-archlinux-${ARCH}-XXXXXXXXXX)
chmod 755 ${ROOTFS}

#-----------------------------------------

pacstrap -C ${TMP_CONF} -c -d -G ${ROOTFS} base-devel haveged

#fakeroot mkdir -p $ROOTFS/var/lib/pacman
#export FAKECHROOT_CMD_SUBST=/usr/bin/ldconfig=/usr/bin/true
#fakechroot fakeroot pacman --root=${ROOTFS} --config=${TMP_CONF} -Sy base-devel haveged


tar --numeric-owner --xattrs --acls -C ${ROOTFS} -c . -f ${DOCKER_IMAGE_NAME}-$(date "+%Y%m%d").tar.gz
ln -sf ${DOCKER_IMAGE_NAME}-$(date "+%Y%m%d").tar.gz ${DOCKER_IMAGE_NAME}-latest.tar.gz
rm -rf ${ROOTFS}
