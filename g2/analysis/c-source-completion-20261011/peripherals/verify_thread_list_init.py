#!/usr/bin/env python3
"""Compare stock/source scheduler list initialization call order and globals."""
from pathlib import Path
import hashlib,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn import arm_const as A
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
SRC=ROOT/'g2/components/audio/thread_new_source_candidate/list_init.c';DATA=ROOT/'g2/components/audio/uart_thread_source_candidate/display_scheduler_ram.c';OTA=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';BLOB=OTA.read_bytes()[0x20:]
OBJ=OUT/'thread-list-init-m4.o';DATAOBJ=OUT/'thread-list-data-m4.o';ELF=OUT/'thread-list-init-m4.elf'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(SRC),'-o',str(OBJ)],check=True)
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-O2','-c',str(DATA),'-o',str(DATAOBJ)],check=True)
subprocess.run(['arm-none-eabi-ld','-Ttext=0x100000','--defsym=vListInitialise=0x101001','-o',str(ELF),str(OBJ),str(DATAOBJ)],check=True)
with ELF.open('rb') as f:
 e=ELFFile(f);SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD'];SY={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
def run(stock):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
 for base,size in ((0x438000,(len(BLOB)+4095)&~4095),(0x100000,0x20000),(0x20000000,0x80000)):u.mem_map(base,size)
 if stock:u.mem_write(0x438000,BLOB)
 else:
  for base,data in SEG:u.mem_write(base,data)
 u.reg_write(A.UC_ARM_REG_SP,0x2007f000);u.reg_write(A.UC_ARM_REG_LR,0x100f01)
 events=[];done=[False]
 def hook(cpu,pc,size,user):
  if pc==0x100f00:done[0]=True;cpu.emu_stop();return
  if pc==(0x45607c if stock else 0x101000):
   events.append(cpu.reg_read(A.UC_ARM_REG_R0));cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR));return
 u.hook_add(UC_HOOK_CODE,hook)
 u.emu_start((0x45568c if stock else SY['g2_thread_initialize_lists'])|1,0,count=5000)
 assert done[0]
 def r(a):return int.from_bytes(u.mem_read(a,4),'little')
 if stock:
  bases=[0x2006a49c,0x20073cfc,0x20073d10,0x20073d24,0x20073d38,0x20073d4c]
  cells=[0x20074a24,0x20074a28]
 else:
  bases=[SY[x] for x in ('g2_audio_ready_lists','g2_audio_delayed_buffer_a','g2_audio_delayed_buffer_b','g2_audio_pending_ready_list','g2_audio_terminated_list','g2_audio_suspended_list')]
  cells=[SY[x] for x in ('g2_audio_delayed_list0','g2_audio_delayed_list1')]
 normalized=[]
 for ptr in events:
  normalized.append((0,(ptr-bases[0])//20) if bases[0]<=ptr<bases[0]+56*20 else (1+bases[1:].index(ptr),0))
 return {'calls':normalized,'delayed_a':r(cells[0])==bases[1],'delayed_b':r(cells[1])==bases[2],'sp':u.reg_read(A.UC_ARM_REG_SP)}
a=run(True);b=run(False)
if a!=b:
 (OUT/'thread-list-init-failure.json').write_text(json.dumps({'stock':a,'source':b},indent=2)+'\n');raise AssertionError('list init')
result={'status':'PASS_THREAD_LIST_INIT_BOUNDED','cases':1,'list_calls':len(a['calls']),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ota_sha256':hashlib.sha256(OTA.read_bytes()).hexdigest(),'limits':'vListInitialise child cut; compares all addresses/order and two delayed-list pointer cells; no scheduler start or initialized list contents.'}
(OUT/'thread-list-init-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(a['calls']))
