#!/usr/bin/env python3
"""Bounded stock/source logger submit through queue child ABI cuts."""
from pathlib import Path
import hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/main/extended_log_runtime_candidate/transport.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'log-transport-m4.o';ELF=OUT/'log-transport-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
assign=['g2_log_transport_node_allocate=0x101001','g2_log_transport_node_enqueue=0x101011','g2_log_transport_node_free=0x101021','g2_log_transport_queue_failure=0x101031','g2_log_transport_queue_failure_message=0x71e990','audio_irq_context=0x101041','g2_log_event_set_task=0x101051','g2_log_event_set_isr=0x101061','g2_log_event_get_bits=0x101071']
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000',*[f'--defsym={x}' for x in assign],'-o',str(ELF),str(OBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);seg=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];sy={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock,enabled,length,level,allocate,enqueued):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in [(0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x10000),(0x20000000,0x80000)]:u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in seg:u.mem_write(base,data)
 u.mem_write(0x20074fc0,bytes([enabled]));u.mem_write(0x20004546,b'\x03')
 u.mem_write(0x20011000,bytes((i&255 for i in range(300))))
 u.mem_write(0x20010000,b'\xaa'*300)
 for reg,val in ((A.UC_ARM_REG_R0,0x20011000),(A.UC_ARM_REG_R1,length),(A.UC_ARM_REG_R2,level),(A.UC_ARM_REG_R3,5),(A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x100f01)):u.reg_write(reg,val)
 names={'alloc':(0x448a0c,0x101000),'enqueue':(0x448af0,0x101010),'free':(0x448a8e,0x101020),'fatal':(0x4733ee,0x101030)}
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  for name,(old,new) in names.items():
   if pc!=(old if stock else new):continue
   events.append([name,None if name=='alloc' else cpu.reg_read(A.UC_ARM_REG_R0)])
   cpu.reg_write(A.UC_ARM_REG_R0,(0x20010000 if allocate else 0) if name=='alloc' else enqueued if name=='enqueue' else 0)
   cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x448d4e if stock else sy['g2_log_transport_submit'])|1,0,count=1500)
 assert done[0]
 return {'events':events,'node':bytes(u.mem_read(0x20010000,300)).hex(),'sp':u.reg_read(A.UC_ARM_REG_SP)}
rows=[]
for enabled,length,level,allocate,enqueued in itertools.product((0,1),(0,1,7,255,300),(0,3),(0,1),(0,1)):
 if not enabled and (length!=7 or level!=0 or not allocate or not enqueued):continue
 if enabled and length==0 and (level!=0 or not allocate or not enqueued):continue
 f=dict(enabled=enabled,length=length,level=level,allocate=allocate,enqueued=enqueued)
 a=run(True,**f);b=run(False,**f)
 if a!=b:
  (OUT/'log-submit-failure.json').write_text(json.dumps({'fixture':f,'stock':a,'source':b},indent=2)+'\n');raise AssertionError(f)
 rows.append({'fixture':f,'result':{'events':a['events'],'sp':a['sp']}})
receipt={'status':'PASS_LOG_SUBMIT_BOUNDED','cases':len(rows),'rows':rows,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'limits':'Allocator, enqueue, free and fatal children cut at named entries. Packet bytes and child ABI compared. Product queue concurrency and transport delivery unverified.'}
(OUT/'log-submit-results.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],len(rows))
