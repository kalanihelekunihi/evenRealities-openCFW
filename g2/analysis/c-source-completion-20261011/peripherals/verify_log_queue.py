#!/usr/bin/env python3
"""Stock/source uncontended node queue transitions; no producer race claim."""
from pathlib import Path
import json,hashlib,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/transport_queue.c'
OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-queue-m4.o'; ELF=OUT/'log-queue-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f); SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']; SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
entries={'allocate':(0x448a0c,'g2_log_transport_node_allocate'),'free':(0x448a8e,'g2_log_transport_node_free'),'enqueue':(0x448af0,'g2_log_transport_node_enqueue')}
def run(stock,kind,initial):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x10000),(0x20000000,0x80000),(0x202e4000,0x1000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 def put(a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
 def get(a):return int.from_bytes(u.mem_read(a,4),'little')
 node=0x20010000; sentinel=0x20011000
 put(node,0);put(node+4,1);put(0x20074574,node if initial else 0)
 put(sentinel,0);put(0x2007413c,sentinel);put(0x20074138,sentinel)
 for a in range(0x2007342c,0x2007345c,4):put(a,0)
 put(0x202e4eb8,0)
 for reg,val in ((A.UC_ARM_REG_R0,node if kind!='allocate' else 0),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((entries[kind][0] if stock else SY[entries[kind][1]])|1,0,count=50000)
 assert done[0],(stock,kind,initial)
 return {'r0':u.reg_read(A.UC_ARM_REG_R0) if kind!='free' else None,'free_head':get(0x20074574),'pending_tail':get(0x2007413c),'node_next':get(node),'node_state':get(node+4),'sentinel_next':get(sentinel),'stats':[get(a) for a in range(0x2007342c,0x2007345c,4)]}
rows=[]
for kind,initial in [('allocate',0),('allocate',1),('free',0),('enqueue',0)]:
 a=run(True,kind,initial);b=run(False,kind,initial)
 if a!=b:
  (OUT/'log-queue-failure.json').write_text(json.dumps({'kind':kind,'initial':initial,'stock':a,'source':b},indent=2)+'\n');raise AssertionError((kind,initial))
 rows.append({'kind':kind,'initial':initial,'result':a})
result={'status':'PASS_LOG_QUEUE_UNCONTENDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'Single-core uncontended path only; no concurrent CAS failures, queue consumer, initialization, or hardware proof.'}
(OUT/'log-queue-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(rows))
