#!/usr/bin/env python3
"""Verify typed CW221X CASE product profile and RAM initializer against CRT."""
from pathlib import Path
import hashlib,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/case_battery_profile_config.c'
compressed=F[0xd95c:0xd95c+104];decoded=bytearray();p=0
while len(decoded)<420:
 h=compressed[p];p+=1;copy=h&15;clear=h>>4
 if copy==0:copy=compressed[p];p+=1
 if clear==0:clear=compressed[p];p+=1
 decoded+=compressed[p:p+copy-1];p+=copy-1;decoded+=bytes(clear-1)
expected=bytes(decoded[0x2a:0x7a])
assert p==104 and len(decoded)==420
assert hashlib.sha256(expected).hexdigest()=='923bf3796afa2e45777f41208c1d9d7ec6f7ac4e3aa9af0984787b9ab05f23ae'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
with tempfile.TemporaryDirectory() as d:
 d=Path(d);o=d/'profile.o';subprocess.run(flags+[str(src),'-o',str(o)],check=True)
 elf=d/'profile.elf';subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x100000',str(o),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
 with elf.open('rb') as f:
  e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 u.mem_map(0x100000,0x10000)
 for a,b in seg:u.mem_write(a,b)
 u.mem_map(0x20000000,0x10000);u.mem_write(0x2000002a,bytes([0x5a])*80)
 u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001)
 u.emu_start(sym['case_crt_init_cw221x_battery_profile']|1,0x20008000,count=3000)
 actual=bytes(u.mem_read(0x2000002a,80));assert actual==expected
 profile=bytes(u.mem_read(sym['case_cw221x_battery_profile'],80));assert profile==expected
 print('PASS_CASE_CW221X_PROFILE',80,hashlib.sha256(profile).hexdigest())
