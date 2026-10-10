set -eu
apt-get update > /out/registered-apt-update.log 2>&1
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential python3 python3-venv meson ninja-build pkg-config libglib2.0-dev libpixman-1-dev libfdt-dev zlib1g-dev > /out/registered-apt-install.log 2>&1
dpkg-query -W > /out/registered-package-versions.txt
mkdir /tmp/qbuild
cd /tmp/qbuild
/src/configure --target-list=cskyv2-softmmu --disable-download --disable-werror --disable-docs --disable-tools --disable-guest-agent --disable-slirp --disable-gtk --disable-sdl --disable-vnc --disable-curses --disable-opengl --disable-virglrenderer > /out/registered-configure.log 2>&1
ninja -j2 qemu-system-cskyv2 > /out/registered-build.log 2>&1
cp qemu-system-cskyv2 /out/qemu-system-cskyv2
./qemu-system-cskyv2 --version > /out/qemu-version.txt
./qemu-system-cskyv2 -cpu help > /out/qemu-cpus.txt
./qemu-system-cskyv2 -machine help > /out/qemu-machines.txt
printf 'PASS\n' > /out/registered-build-status.txt
exec sleep infinity
