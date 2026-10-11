#!/usr/bin/env python3
"""Stock/source event-group bit getter with selected BASEPRI helpers executing."""
from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/event_get.c';MASK=ROOT/'g2/components/audio/source_candidate_20261010/irq_mask_pair.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
objs=[]
for i,p in enumerate((SRC,MASK)):
 o=OUT/f'event-get-{i}.o';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-c',str(p),'-o',str(o)],check=True);objs.append(o)
elf=OUT/'event-get.elf';subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(elf),*map(str,objs)],check=True)
with elf.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for basepri,bits in itertools.product((0,0x10,0x30,0x80),(0,1,0x12345678,0xffffffff)):
 results=[]
 for stock in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
  for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x10000),(0x20000000,0x10000)):u.mem_map(base,size)
  if stock:u.mem_write(0x438000,BLOB)
  else:
   for base,data in seg:u.mem_write(base,data)
  u.mem_write(0x20001000,bits.to_bytes(4,'little'))
  u.reg_write(A.UC_ARM_REG_R0,0x20001000);u.reg_write(A.UC_ARM_REG_SP,0x20008000);u.reg_write(A.UC_ARM_REG_LR,0x100f01);u.reg_write(A.UC_ARM_REG_BASEPRI,basepri)
  u.emu_start((0x47ed64 if stock else sy['g2_log_event_get_bits'])|1,0x100f00,count=70)
  results.append((u.reg_read(A.UC_ARM_REG_R0),u.reg_read(A.UC_ARM_REG_BASEPRI),u.reg_read(A.UC_ARM_REG_SP)))
 assert results[0]==results[1]==(bits,basepri,0x20008000)
 rows.append({'basepri':basepri,'bits':bits})
receipt={'status':'PASS_EVENT_GET','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'mask_source_sha256':hashlib.sha256(MASK.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elf.read_bytes()).hexdigest(),'limits':'Synthetic event-group first word and BASEPRI; no concurrent waiters or task scheduling.'}
(OUT/'log-event-get-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
