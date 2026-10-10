set -eu
python3 -m venv /tmp/lz4env
/tmp/lz4env/bin/python -m pip install --disable-pip-version-check unicorn==2.1.4 capstone==5.0.7 pyelftools==0.32 > /out/python-dependencies.log 2>&1
/tmp/lz4env/bin/python -m pip freeze > /out/python-dependency-versions.txt
/tmp/lz4env/bin/python -u -c 'from unicorn import *; from unicorn.arm_const import *; u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x1000,0x1000);u.mem_write(0x1000,bytes([7,32,112,71]));u.reg_write(UC_ARM_REG_LR,0x1101);u.emu_start(0x1001,0x1100,count=2);print("ARM Thumb engine smoke R0",u.reg_read(UC_ARM_REG_R0))' > /out/linux-engine-smoke.txt 2>&1
for version in v1.9.4 v1.10.0; do gcc -O2 -fPIC -shared -I/out/$version /out/$version/lz4.c -o /out/$version/liblz4.so; done
gcc --version > /out/linux-gcc-version.txt
printf 'PASS\n' > /out/linux-setup-status.txt
exec sleep infinity
