"""Actual compiled ARM C/native radio acquisition branch and state comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_acquire.c'
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_radio_resource_state_20073dc4[24];
const uint8_t audio_ble_hci_radio_resource_config_200001b4[20]={0};
volatile uint32_t audio_ble_hci_radio_revision_word_20074224;
const uint8_t audio_ble_hci_radio_resource_log_768a90[1]={0};
const uint8_t audio_ble_hci_radio_resource_log5_77d90c[1]={0};
const uint8_t audio_ble_hci_radio_resource_revision_log_768aac[1]={0};
void audio_ble_hci_boot_log_4733ee(const void*p,...){(void)p;}
void audio_ble_radio_power_config_4c2b68(uint32_t a,uint32_t b){(void)a;(void)b;}
void audio_ble_radio_platform_init_52dc40(void){}
int32_t audio_ble_radio_stack_open_55c2bc(uint32_t a,void*b){(void)a;(void)b;return 0;}
int32_t audio_ble_radio_stack_option_55c7e8(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
int32_t audio_ble_radio_stack_config_55ca94(uint32_t a,const void*b){(void)a;(void)b;return 0;}
int32_t audio_ble_radio_stack_start_55c32e(uint32_t a){(void)a;return 0;}
void audio_ble_radio_context_init_52e0a2(void*p){(void)p;}
int32_t audio_ble_radio_context_check_52e4b4(void*p){(void)p;return 0;}
void audio_ble_radio_context_recover_52f0f8(void*p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;}
int32_t audio_ble_radio_read_revision_52eeea(void*p,volatile uint32_t*r){(void)p;(void)r;return 0;}
void audio_ble_radio_dispatch_set_52edd8(uint32_t x){(void)x;}
'''
NATIVE={'power':0x4c2b68,'init':0x52dc40,'open':0x55c2bc,'option':0x55c7e8,'config':0x55ca94,'start':0x55c32e,'ctxinit':0x52e0a2,'check':0x52e4b4,'log':0x4733ee,'recover':0x52f0f8,'revision':0x52eeea,'dispatch':0x52edd8}
CNAME={'power':'audio_ble_radio_power_config_4c2b68','init':'audio_ble_radio_platform_init_52dc40','open':'audio_ble_radio_stack_open_55c2bc','option':'audio_ble_radio_stack_option_55c7e8','config':'audio_ble_radio_stack_config_55ca94','start':'audio_ble_radio_stack_start_55c32e','ctxinit':'audio_ble_radio_context_init_52e0a2','check':'audio_ble_radio_context_check_52e4b4','log':'audio_ble_hci_boot_log_4733ee','recover':'audio_ble_radio_context_recover_52f0f8','revision':'audio_ble_radio_read_revision_52eeea','dispatch':'audio_ble_radio_dispatch_set_52edd8'}
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_radio_acquire_52dd94',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for label,busy,kind,failed,checkval in [('busy',1,6,'',0),('badkind',0,9,'',0),('null',0,6,'null',0),('openfail',0,6,'open',0),('optionfail',0,6,'option',0),('configfail',0,6,'config',0),('startfail',0,6,'start',0),('success0',0,6,'',0),('success5',0,6,'',5),('success2',0,6,'',2)]:
  rows=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   state=syms['audio_ble_hci_radio_resource_state_20073dc4'] if is_c else 0x20073dc4
   rev=syms['audio_ble_hci_radio_revision_word_20074224'] if is_c else 0x20074224
   u.mem_write(state,b'\x00'*24);u.mem_write(state+8,bytes([busy]));u.mem_write(rev,struct.pack('<I',0xffffffff))
   if not is_c:u.mem_write(0x200001b4,b'\x00'*20)
   u.mem_write(0x20006000,struct.pack('<II',0x200703ec,0x40));u.mem_write(0x20006100,b'\x00'*8)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,kind);u.reg_write(UC_ARM_REG_R1,0 if failed=='null' else 0x20006000);u.reg_write(UC_ARM_REG_R2,0x20006100);u.reg_write(UC_ARM_REG_R3,0x20006104)
   cuts={v:k for k,v in (NATIVE if not is_c else {k:syms[n]&~1 for k,n in CNAME.items()}).items()};calls=[]
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];val=0
    if name=='open':
     uc.mem_write(uc.reg_read(UC_ARM_REG_R1),struct.pack('<I',0x12340000))
    if name=='config':calls.append((name,bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),20))))
    elif name=='recover':calls.append((name,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
    elif name=='revision':calls.append((name,));uc.mem_write(uc.reg_read(UC_ARM_REG_R1),struct.pack('<I',0x01020304))
    elif name=='log':calls.append((name,uc.reg_read(UC_ARM_REG_R1)))
    else:calls.append((name,))
    if name==failed:val=1
    if name=='check':val=checkval
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_radio_acquire_52dd94'] if is_c else 0x52dd94)|1,0x600000,count=1000)
   ctx,stack=struct.unpack('<II',u.mem_read(0x20006100,8));ctx=(ctx-state)&0xffffffff if ctx else 0
   rows.append((u.reg_read(UC_ARM_REG_R0),[(c[0],*c[1:]) for c in calls],bytes(u.mem_read(state,12)),ctx,stack,bytes(u.mem_read(rev,4))))
  assert rows[0]==rows[1],(label,rows)
  print('PASS',label,rows[0][0],[c[0] for c in rows[0][1]])
