"""Connected settings/HUB C versus original paths with sender boundary."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CASES=[('open_mode_gate','open',1,1,1,0),('open_disabled','open',0,0,1,0),
       ('open_wrong_role','open',0,1,0,0),('open_master','open',0,1,1,0),
       ('open_hub_left','open',0,1,1,2),('close_mode_gate','close',1,1,1,0),
       ('close_wrong_role','close',0,1,0,0),('close_master','close',0,1,1,0),
       ('close_hub_left','close',0,1,1,2),
       ('open_disabled_log2','open',0,0,1,0),
       ('open_wrong_role_log2','open',0,1,0,0),
       ('open_hub_left_log2','open',0,1,1,2),
       ('close_wrong_role_log2','close',0,1,0,0),
       ('open_queue_fail_log2','open',0,1,1,0),
       ('close_queue_fail_log2','close',0,1,1,0),
       ('role_init_master','role_init',0,0,1,9),
       ('role_init_slave','role_init',0,0,2,9),
       ('role_init_other','role_init',0,0,0,9),
       ('configure_on_worn','configure',1,0,1,1),
       ('configure_on_notworn','configure',1,0,1,0),
       ('configure_off','configure',0,1,1,0)]
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text('''#include <stdint.h>
volatile uint16_t audio_uart_hub_role_cell;
void *audio_hub_send_queue;
int32_t g_queue_result;
uint32_t g_wear;
uint32_t audio_log_wake_allowed(void){return g_wear;}
uint32_t audio_uart_command_pending(void){return *(volatile uint8_t *)0x200038f1u;}
uint8_t audio_uart_device_role_get(void){return *(volatile uint8_t *)0x20075024u;}
uint32_t audio_uart_wear_status(void){return g_wear;}
uint32_t audio_log_flags(void){return *(volatile uint8_t *)0x20004543u;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)b;(void)c;(void)d;(void)f;volatile uint32_t *out=(volatile uint32_t *)0x20090010u;out[0]++;out[1]=a;out[2]=e;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_cmsis_queue_put(void *q,const void *p,uint8_t priority,uint32_t timeout){(void)q;(void)priority;(void)timeout;const uint8_t *s=p;volatile uint8_t *d=(volatile uint8_t *)0x20090000u;for(unsigned i=0;i<8;i++)d[i]=s[i];return g_queue_result;}
''')
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,SVC_Settings_AutoBrightnessOpen',str(ROOT/'components/audio/uart_thread_source_candidate/display_auto_brightness.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_hub_channel.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_hub_send.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_hub_role_init.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_auto_brightness_configure.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_auto_brightness_state.c'),str(shim),'-o',str(elf)],check=True)
 symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,case):
  label,operation,mode,enabled,role,hub_role=case
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_map(0x20000000,0x100000)
  u.mem_write(0x200038f1,bytes([mode]));u.mem_write(0x20072daa,bytes([enabled]))
  u.mem_write(0x20072dac,struct.pack('<I',7))
  u.mem_write(0x20075024,bytes([role]));u.mem_write(0x20004526,struct.pack('<H',hub_role))
  u.mem_write(0x20003670,struct.pack('<I',0x20060000))
  u.mem_write(symbols['audio_hub_send_queue'],struct.pack('<I',0x20060000))
  u.mem_write(symbols['g_queue_result'],struct.pack('<i',-3 if 'queue_fail' in label else 0))
  u.mem_write(0x20004543,bytes([2 if label.endswith('log2') else 0]))
  u.mem_write(symbols['audio_uart_auto_brightness_enabled_cell'],bytes([enabled]))
  u.mem_write(symbols['audio_uart_auto_brightness_profile_cell'],struct.pack('<I',7))
  u.mem_write(symbols['audio_uart_hub_role_cell'],struct.pack('<H',hub_role))
  u.mem_write(symbols['g_wear'],struct.pack('<I',hub_role if operation=='configure' else 0))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  if operation=='configure':u.reg_write(UC_ARM_REG_R0,mode)
  if not candidate:
   def send_cut(uc,address,size,_):
    if address==0x449abe:
     payload=bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),8))
     uc.mem_write(0x20090000,payload)
     uc.reg_write(UC_ARM_REG_R0,0xfffffffd if 'queue_fail' in label else 0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     return
    elif address==0x43d574:
     count=struct.unpack('<I',uc.mem_read(0x20090010,4))[0]+1
     line=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
     uc.mem_write(0x20090010,struct.pack('<III',count,uc.reg_read(UC_ARM_REG_R0),line))
    elif address==0x443484 and operation=='configure':
     uc.reg_write(UC_ARM_REG_R0,hub_role)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     return
    else:return
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,send_cut)
  names={'open':'SVC_Settings_AutoBrightnessOpen','close':'SVC_Settings_AutoBrightnessClose','role_init':'audio_hub_role_init','configure':'audio_uart_auto_brightness_configure'}
  originals={'open':0x46c01c,'close':0x46c0e8,'role_init':0x4a6d28,'configure':0x46c158}
  entry=symbols[names[operation]] if candidate else originals[operation]
  u.emu_start(entry|1,0x600000,count=2000)
  role_value=bytes(u.mem_read(symbols['audio_uart_hub_role_cell'] if candidate else 0x20004526,2))
  enabled_value=bytes(u.mem_read(symbols['audio_uart_auto_brightness_enabled_cell'] if candidate else 0x20072daa,1))
  profile_value=bytes(u.mem_read(symbols['audio_uart_auto_brightness_profile_cell'] if candidate else 0x20072dac,4))
  result=None if operation=='role_init' else u.reg_read(UC_ARM_REG_R0)
  return result,bytes(u.mem_read(0x20090000,8)),bytes(u.mem_read(0x20090010,12)),role_value,enabled_value,profile_value
 for case in CASES:
  a=run(False,case);b=run(True,case)
  assert a==b,(case[0],a,b)
  print('PASS auto brightness',case[0])
