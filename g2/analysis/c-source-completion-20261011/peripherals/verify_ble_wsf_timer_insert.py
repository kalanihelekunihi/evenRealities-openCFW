"""Actual ARM C/native WSF timer sorted insertion and queue ownership."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_wsf_timer_insert.c'
SHIM='''#include <stdint.h>
uint32_t audio_wsf_timer_list[2];
void WsfTaskLock(void){}void WsfTaskUnlock(void){}void audio_wsf_timer_remove(void*p){(void)p;}
void audio_wsf_cs_enter(void){}void audio_wsf_cs_exit(void){}
void audio_wsf_queue_enqueue(void*q,void*e){uint32_t*a=q;uint32_t*p=e;*p=0;if(a[0]==0)a[0]=(uint32_t)e;else *(uint32_t*)a[1]=(uint32_t)e;a[1]=(uint32_t)e;}
'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_wsf_timer_insert',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,ticks,chain in (('empty',10,()),('front',5,(10,20)),('middle',15,(10,20)),('tail',25,(10,20)),('equal',10,(10,20))):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   queue=syms['audio_wsf_timer_list'] if is_c else 0x200741b0
   nodes=[0x20006000,0x20006100,0x20006200];new=nodes[2]
   u.mem_write(queue,struct.pack('<II',nodes[0] if chain else 0,nodes[len(chain)-1] if chain else 0))
   for i,when in enumerate(chain):u.mem_write(nodes[i],struct.pack('<II',nodes[i+1] if i+1<len(chain) else 0,when)+bytes(8))
   u.mem_write(new,bytes(16))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,new);u.reg_write(UC_ARM_REG_R1,ticks)
   native={0x52b8c8:'lock',0x52b8d0:'unlock',0x52b8a4:'cs',0x52b8b6:'cs'}
   compiled={syms['WsfTaskLock']&~1:'lock',syms['WsfTaskUnlock']&~1:'unlock',syms['audio_wsf_cs_enter']&~1:'cs',syms['audio_wsf_cs_exit']&~1:'cs'}
   cuts=compiled if is_c else native;calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    calls.append(cuts[a]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_wsf_timer_insert'] if is_c else 0x52a424)|1,0x600000,count=600)
   results.append((bytes(u.mem_read(queue,8)),*[bytes(u.mem_read(n,16)) for n in nodes]))
  assert results[0]==results[1],(label,results)
  print('PASS',label)
