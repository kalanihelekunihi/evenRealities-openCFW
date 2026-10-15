"""Bounded ARM C/native HciDrvRadioBoot call/flag effect comparison."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_boot.c'
DATA='audio_ble_hci_radio_boot_config audio_ble_hci_radio_context_ptr audio_ble_hci_radio_aux_ptr audio_ble_hci_radio_boot_retry audio_ble_hci_radio_revision_cell audio_ble_hci_radio_active audio_ble_hci_radio_pending audio_ble_hci_radio_command_cell audio_ble_hci_radio_driver_state audio_ble_hci_radio_scheduler_state audio_ble_hci_radio_scheduler_config audio_ble_hci_boot_log_first audio_ble_hci_boot_log_retry'.split()
FUNS={'audio_ble_hci_radio_acquire_52dd94':0x52dd94,'audio_ble_hci_radio_detect_52deee':0x52deee,'audio_ble_hci_boot_log_4733ee':0x4733ee,'audio_ble_hci_boot_delay_491102':0x491102,'audio_ble_hci_radio_prepare_52f38c':0x52f38c,'audio_ble_hci_radio_validate_52fcfc':0x52fcfc,'audio_ble_hci_radio_revision_52dee6':0x52dee6,'audio_ble_hci_radio_revision_mismatch_4b47cc':0x4b47cc,'audio_ble_hci_radio_recover_52fb58':0x52fb58,'audio_ble_hci_radio_reconfigure_4b480a':0x4b480a,'audio_ble_hci_radio_finalize_52fc04':0x52fc04,'audio_ble_hci_radio_scheduler_53006c':0x53006c,'audio_ble_hci_radio_identifier_480d72':0x480d72,'audio_ble_hci_radio_register_48162c':0x48162c,'audio_ble_hci_radio_enable_52dd58':0x52dd58,'audio_ble_hci_radio_mux_on_4b4786':0x4b4786,'audio_ble_hci_radio_mux_request_4b4768':0x4b4768}
SHIM='''#include <stdint.h>
uint8_t audio_ble_hci_radio_boot_config[8],audio_ble_hci_radio_driver_state[16],audio_ble_hci_radio_scheduler_state[16],audio_ble_hci_radio_scheduler_config[16];
uint32_t audio_ble_hci_radio_context_ptr,audio_ble_hci_radio_aux_ptr,audio_ble_hci_radio_revision_cell,audio_ble_hci_radio_active,audio_ble_hci_radio_pending,audio_ble_hci_radio_command_cell;
uint8_t audio_ble_hci_radio_boot_retry;
const uint8_t audio_ble_hci_boot_log_first[8]={0},audio_ble_hci_boot_log_retry[8]={0};
void opencfw_radio_gpio_callback(void *argument){(void)argument;}
void __aeabi_memcpy(void*d,const void*s,unsigned n){uint8_t*a=d;const uint8_t*b=s;for(unsigned i=0;i<n;i++)a[i]=b[i];}
''' + '\n'.join('void '+n+'(){ }' for n in FUNS)+'\n'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text(SHIM);elf=Path(td)/'a.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_hci_driver_radio_boot',str(SRC),str(p),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 native={v:k for k,v in FUNS.items()};compiled={syms[k]&~1:k for k in FUNS}
 for label,detect,validate,mismatch in (('normal',0,0,0),('detected',1,0,0),('validate_same',0,1,0),('revision_retry',0,1,1),('identifier',0,0,0)):
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   cells={'retry':syms['audio_ble_hci_radio_boot_retry'] if is_c else 0x20074fcc,'active':syms['audio_ble_hci_radio_active'] if is_c else 0x20074638,'pending':syms['audio_ble_hci_radio_pending'] if is_c else 0x2007463c,'command':syms['audio_ble_hci_radio_command_cell'] if is_c else 0x20074640,'context':syms['audio_ble_hci_radio_context_ptr'] if is_c else 0x20074630,'revision':syms['audio_ble_hci_radio_revision_cell'] if is_c else 0x20074954}
   u.mem_write(cells['revision'],struct.pack('<I',4));u.mem_write(cells['active'],struct.pack('<I',8));u.mem_write(cells['pending'],struct.pack('<I',9));u.mem_write(cells['command'],struct.pack('<I',10))
   driver=syms['audio_ble_hci_radio_driver_state'] if is_c else 0x20074148
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1 if label=='identifier' else 0)
   calls=[];detect_count=[0];cuts=compiled if is_c else native
   def hook(uc,a,size,_):
    if a not in cuts:return
    name=cuts[a];calls.append(name)
    val=0
    if name.endswith('acquire_52dd94'):val=0x20005100
    elif name.endswith('detect_52deee'):
     detect_count[0]+=1;val=detect
    elif name.endswith('validate_52fcfc'):val=validate
    elif name.endswith('revision_52dee6'):val=4
    elif name.endswith('revision_mismatch_4b47cc'):val=mismatch
    elif name.endswith('identifier_480d72'):
     uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes(range(16)))
    elif name.endswith('register_48162c'):
     observed=uc.reg_read(UC_ARM_REG_R2)
     expected=(syms['opencfw_radio_gpio_callback']|1) if is_c else 0x4b4a99
     assert observed==expected,(is_c,hex(observed),hex(expected))
    uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((syms['audio_ble_hci_driver_radio_boot'] if is_c else 0x4b48a6)|1,0x600000,count=1100)
   results.append((u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(cells['retry'],1)),*(struct.unpack('<I',u.mem_read(cells[k],4))[0] for k in ('active','pending','command')),bytes(u.mem_read(driver,6))))
  assert results[0]==results[1],(label,results)
  print('PASS',label,results[0][0],len(results[0][1]))
