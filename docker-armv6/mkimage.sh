#!/bin/bash

ARCH='armv6h'
DOCKER_IMAGE_NAME="archlinux-${ARCH}"
PACMAN_CONF="./pacman-armv6h.conf"

ROOTFS=$(mktemp -d ${TMPDIR:-/var/tmp}/rootfs-archlinux-${ARCH}-XXXXXXXXXX)
chmod 755 ${ROOTFS}

#-----------------------------------------

pacstrap -C ${PACMAN_CONF} -c -d -G ${ROOTFS} base-devel haveged

#fakeroot mkdir -p $ROOTFS/var/lib/pacman
#export FAKECHROOT_CMD_SUBST=/usr/bin/ldconfig=/usr/bin/true
#fakechroot fakeroot pacman --root=${ROOTFS} --config=${TMP_CONF} -Sy base-devel haveged


tar --numeric-owner --xattrs --acls -C ${ROOTFS} -c . -f $DOCKER_IMAGE_NAME-$(date "+%Y%m%d").tar.gz
ln -sf $DOCKER_IMAGE_NAME-$(date "+%Y%m%d").tar.gz $DOCKER_IMAGE_NAME-latest.tar.gz
rm -rf ${ROOTFS}
