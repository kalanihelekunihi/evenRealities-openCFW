"""Actual ARM compiled-C/native ATT assertion terminal-effect comparisons."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate'
SHIM='''#include <stdint.h>
uint8_t audio_ble_att_runtime[128],audio_ble_registration_records[1024],audio_ble_connection_records[512],audio_ble_connection_state_table[128];
volatile uint8_t audio_ble_trace_level_cell;
uint32_t g2_smp_candidate_compare(void *c,uint32_t a,uint32_t b,uint32_t n){(void)c;(void)a;(void)b;(void)n;return 0;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
void audio_ble_wsf_trace(const char*a,const char*b,...){(void)a;(void)b;}
'''
def cstr(u,a):
 if not a:return ''
 b=bytes(u.mem_read(a,160));return b.split(b'\0')[0].decode('latin1')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 sources=[SRC/x for x in ('display_ble_att_assert_paths.c','display_ble_att_ccb_valid.c','display_ble_att_registration_valid.c','display_ble_att_connection_valid.c')]
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_att_ccb_by_conn_id',*[str(x) for x in sources],str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for scenario in ('ccb_zero','reg_zero','reg_invalid','valid_zero'):
  for level in (0,1):
   rows=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_write(syms['audio_ble_trace_level_cell'] if compiled else 0x2007502f,bytes([level]))
    u.reg_write(UC_ARM_REG_R0,2 if scenario=='reg_invalid' else 0)
    u.reg_write(UC_ARM_REG_R1,0x824)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    calls=[]
    cuts={(syms['g2_smp_candidate_compare']&~1 if compiled else 0x44b610):'compare',
          (syms['audio_log_flags']&~1 if compiled else 0x43d0ce):'flags',
          (syms['audio_log_extended']&~1 if compiled else 0x43d574):'log',
          (syms['audio_ble_wsf_trace']&~1 if compiled else 0x52a63c):'trace'}
    if not compiled:cuts[0x4c9c50]='policy'
    def hook(uc,a,size,_):
     if a not in cuts:return
     kind=cuts[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
     if kind=='compare':
      if compiled:r0,r1,n=r1,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)
      else:n=uc.reg_read(UC_ARM_REG_R2)
      x=bytes(uc.mem_read(r0,n));y=bytes(uc.mem_read(r1,n));res=0 if x==y or b'\0' in x and x.split(b'\0')[0]==y.split(b'\0')[0] else (1 if x>y else 0xffffffff)
     elif kind=='policy':res=level
     elif kind=='flags':res=2
     elif kind=='log':
      calls.append(('log',r0,cstr(uc,r1),cstr(uc,uc.reg_read(UC_ARM_REG_R2)),cstr(uc,uc.reg_read(UC_ARM_REG_R3))));res=0
     else:calls.append(('trace',cstr(uc,r0),cstr(uc,r1)));res=0
     uc.reg_write(UC_ARM_REG_R0,res);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    name={'ccb_zero':'audio_ble_att_ccb_by_conn_id','reg_zero':'audio_ble_att_registration_lookup','reg_invalid':'audio_ble_att_registration_lookup','valid_zero':'audio_ble_att_connection_valid'}[scenario]
    native={'ccb_zero':0x4b4eee,'reg_zero':0x534f14,'reg_invalid':0x534f14,'valid_zero':0x52c928}[scenario]
    u.emu_start((syms[name] if compiled else native)|1,0x600000,count=2500)
    rows.append((calls,u.reg_read(UC_ARM_REG_R0)))
   assert rows[0]==rows[1],(scenario,level,rows)
   print('PASS',scenario,level,rows[0])
