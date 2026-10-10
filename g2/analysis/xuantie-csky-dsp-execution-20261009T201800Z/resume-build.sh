set -eu
apt-get update > /out/resume-apt-update.log 2>&1
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends git ca-certificates > /out/resume-apt-install.log 2>&1
mkdir /tmp/qsrc
(cd /src && tar --exclude=.git -cf - .) | tar -xf - -C /tmp/qsrc
mkdir /tmp/qbuild2
cd /tmp/qbuild2
/tmp/qsrc/configure --target-list=cskyv2-softmmu --disable-werror --disable-docs --disable-tools --disable-guest-agent --disable-slirp --disable-gtk --disable-sdl --disable-vnc --disable-curses --disable-opengl --disable-virglrenderer > /out/resume-configure.log 2>&1
ninja -j2 qemu-system-cskyv2 > /out/resume-build.log 2>&1
cp qemu-system-cskyv2 /out/qemu-system-cskyv2
./qemu-system-cskyv2 --version > /out/qemu-version.txt
./qemu-system-cskyv2 -cpu help > /out/qemu-cpus.txt
./qemu-system-cskyv2 -machine help > /out/qemu-machines.txt
printf 'PASS\n' > /out/resume-build-status.txt
exec sleep infinity
