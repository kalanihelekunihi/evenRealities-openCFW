from pathlib import Path
import subprocess,json
r=Path('/Users/kalani/Repo/evenRealities-openCFW');d=r/'g2/analysis/xuantie-csky-dsp-execution-20261009T201800Z';b=r/'g2/build/offline-xuantie-csky-dsp-20261009T201800Z'
script='''set -eu
apt-get update > /out/apt-update.log 2>&1
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential python3 python3-venv meson ninja-build pkg-config libglib2.0-dev libpixman-1-dev libfdt-dev zlib1g-dev curl ca-certificates > /out/apt-install.log 2>&1
dpkg-query -W > /out/build-package-versions.txt
curl -fL https://codeload.github.com/XUANTIE-RV/qemu/tar.gz/3287d345c7f5d60d5c8774d90752f5f710744f85 -o /work/source.tar.gz > /out/source-fetch.log 2>&1
sha256sum /work/source.tar.gz > /out/source-archive-sha256.txt
mkdir /work/source /work/build
tar -xzf /work/source.tar.gz -C /work/source --strip-components=1
cd /work/build
/work/source/configure --target-list=cskyv2-softmmu --disable-download --disable-werror --disable-docs --disable-tools --disable-guest-agent --disable-slirp --disable-gtk --disable-sdl --disable-vnc --disable-curses --disable-opengl --disable-virglrenderer > /out/configure.log 2>&1
ninja -j2 qemu-system-cskyv2 > /out/build.log 2>&1
./qemu-system-cskyv2 --version > /out/qemu-version.txt
./qemu-system-cskyv2 -cpu help > /out/qemu-cpus.txt
./qemu-system-cskyv2 -machine help > /out/qemu-machines.txt
'''
(d/'build-container.sh').write_text(script)
cmd=['/opt/homebrew/bin/docker','run','--rm','--platform','linux/arm64','--mount',f'type=bind,src={b},dst=/work','--mount',f'type=bind,src={d},dst=/out','ubuntu:24.04','/bin/sh','/out/build-container.sh'];q=subprocess.run(cmd,capture_output=True,text=True);(d/'build-receipt.json').write_text(json.dumps({'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'source_pin':'3287d345c7f5d60d5c8774d90752f5f710744f85'},indent=2)+'\n');print(q.returncode,q.stderr,flush=True)
