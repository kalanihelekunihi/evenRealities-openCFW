#!/usr/bin/env python3
"""Compare stock/source logger transport initializer and 256-node RAM pool."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/transport_init.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-init-m4.o';ELF=OUT/'log-init-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,enabled):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000),(0x202d3000,0x13000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 pool=0x202d3fc8;u.mem_write(pool,b'\xaa'*(256*272))
 u.mem_write(0x2007342c,b'\xaa'*48)
 u.mem_write(0x20074fc0,bytes([enabled]));u.mem_write(0x20004546,b'\xaa')
 for reg,val in ((A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x448c74 if stock else SY['g2_log_transport_initialize'])|1,0,count=2000000)
 assert done[0],(stock,enabled)
 def word(a):return int.from_bytes(u.mem_read(a,4),'little')
 raw=bytes(u.mem_read(pool,256*272))
 return {'pool_hash':hashlib.sha256(raw).hexdigest(),'first_next':word(pool),'node253_next':word(pool+253*272),'node254_next':word(pool+254*272),'node255_next':word(pool+255*272),'free_head':word(0x20074574),'pending_head':word(0x20074138),'pending_tail':word(0x2007413c),'stats':bytes(u.mem_read(0x2007342c,48)).hex(),'enabled':bytes(u.mem_read(0x20074fc0,1)).hex(),'default_level':bytes(u.mem_read(0x20004546,1)).hex()}
rows=[]
for enabled in (0,1):
 a=run(True,enabled);b=run(False,enabled)
 if a!=b:
  (OUT/'log-init-failure.json').write_text(json.dumps({'enabled':enabled,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(enabled)
 rows.append({'enabled':enabled,'result':a})
receipt={'status':'PASS_LOG_INIT_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'Single-threaded initializer with seeded RAM; compares full 256-node pool and globals; no reset order/concurrent use/hardware proof.'}
(OUT/'log-init-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
