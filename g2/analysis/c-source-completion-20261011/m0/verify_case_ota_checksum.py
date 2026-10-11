#!/usr/bin/env python3
"""Native/source CASE 0x9b70 packet checksum comparison."""
from pathlib import Path
import random,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[3]
F=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
src=R/'g2/components/case/startup_candidate_20261011/application_policy_ota_set_mode_candidate.c';obj=H/'ota_checksum.oracle.o';stub=H/'ota_checksum.oracle_stub.c';stubobj=H/'ota_checksum.oracle_stub.o';elf=H/'ota_checksum.oracle.elf'
flags=['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c']
subprocess.run(flags+[str(src),'-o',str(obj)],check=True)
stub.write_text('#include <stdint.h>\nconst uint8_t case_policy_ota_probe_template[12]={0};\nvoid case_policy_sensor_delay(uint32_t a){(void)a;}\nuint32_t case_legacy_logger(const char*a,...){(void)a;return 0;}\nuint32_t case_policy_ota_transmit(uint32_t a,const uint8_t*b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\nuint32_t case_policy_parse_probe(uint32_t a){return a;}\n')
subprocess.run(flags+[str(stub),'-o',str(stubobj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),str(stubobj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(p['p_vaddr'],p.data()) for p in e.iter_segments() if p['p_type']=='PT_LOAD']
rng=random.Random(0x9b70)
for i in range(96):
 size=1+i%16;data=bytes(rng.randrange(256) for _ in range(32));pair=[]
 for native in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(F)+4095)&~4095);u.mem_write(0x08000000,F)
  u.mem_map(0x00100000,0x10000)
  for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,data)
  u.reg_write(UC_ARM_REG_SP,0x20007fc0);u.reg_write(UC_ARM_REG_LR,0x20008001);u.reg_write(UC_ARM_REG_R0,0x20002000);u.reg_write(UC_ARM_REG_R1,size)
  u.emu_start((0x08009b70 if native else sym['case_policy_ota_checksum'])|1,0x20008000,count=500)
  pair.append(bytes(u.mem_read(0x20002000,32)))
 assert pair[0]==pair[1],(i,pair)
print('PASS_CASE_OTA_CHECKSUM',96)
