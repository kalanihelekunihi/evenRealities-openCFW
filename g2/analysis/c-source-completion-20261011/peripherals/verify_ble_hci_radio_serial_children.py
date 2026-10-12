"""Actual ARM C/native radio select/release/mode and shifter effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_hci_radio_serial_children.c'
W=lambda u,a,v:u.mem_write(a,struct.pack('<I',v))
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'shim.c';p.write_text('''#include <stdint.h>\nvolatile uint8_t audio_ble_hci_radio_dispatch_cell_20074f4f;\nvolatile uint8_t audio_ble_radio_mode_cell_20074f53;\nuint32_t audio_ble_radio_stack_option_55c7e8(uint32_t a,uint32_t b,uint32_t c){return 0;}\nuint32_t audio_ble_radio_stack_start_55c32e(uint32_t a){return 0;}\nvoid audio_ble_hci_boot_delay_491102(uint32_t n){}\nint32_t g2_gpio_hal_write(uint32_t a,uint32_t b){return 0;}\n''')
 e=Path(td)/'a.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_radio_begin_select_52e072',str(S),str(p),'-o',str(e)],check=True)
 syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(e)],text=True).splitlines() if len(v:=l.split())==3}
 with e.open('rb') as f:segs=[(x['p_vaddr'],x.data()) for x in ELFFile(f).iter_segments() if x['p_type']=='PT_LOAD']
 entries={'select':('audio_ble_radio_begin_select_52e072',0x52e072),'release':('audio_ble_radio_tx_release_52e058',0x52e058),'mode':('audio_ble_radio_io_mode_52dd1c',0x52dd1c),'put':('audio_ble_radio_serial_put_52dc98',0x52dc98),'get':('audio_ble_radio_serial_get_52dcde',0x52dcde)}
 child={'option':('audio_ble_radio_stack_option_55c7e8',0x55c7e8),'start':('audio_ble_radio_stack_start_55c32e',0x55c32e),'delay':('audio_ble_hci_boot_delay_491102',0x491102),'gpio':('g2_gpio_hal_write',0x480fd6)}
 cases=[('select_bad','select',0,0,0),('select_busy','select',1,1,0),('select_ok','select',1,0,0),('release','release',0,0,0),('mode0','mode',0,0,0),('mode1','mode',0,0,1),('put80','put',0,0,0x80),('put55','put',0,0,0x55),('get0','get',0,0,0),('get1','get',0,0,0x40000000)]
 for name,kind,active,busy,value in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x10000)
   for a,d in segs:u.mem_write(a,d)
   ctx=0x20001000;u.mem_write(ctx,b'\x00'*16);W(u,ctx+4,0x1234);u.mem_write(ctx+8,bytes([active,busy]))
   flag=syms['audio_ble_hci_radio_dispatch_cell_20074f4f'] if is_c else 0x20074f4f
   modecell=syms['audio_ble_radio_mode_cell_20074f53'] if is_c else 0x20074f53
   u.mem_write(flag,b'\x01');u.mem_write(modecell,bytes([value&0xff]));W(u,0x40010408,value)
   calls=[];writes=[];cuts={((syms[s]&~1) if is_c else addr):key for key,(s,addr) in child.items()}
   def hook(uc,a,size,_):
    key=cuts.get(a)
    if key is None:return
    calls.append((key,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if key in ('option','gpio') else 0,uc.reg_read(UC_ARM_REG_R2) if key=='option' else 0))
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def memhook(uc,access,a,size,v,_):
    if a in (0x40010440,0x4001045c):writes.append((a,v))
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,memhook)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ctx if kind in ('select','release') else value)
   entry=syms[entries[kind][0]] if is_c else entries[kind][1]
   u.emu_start(entry|1,0x600000,count=300)
   returned=u.reg_read(UC_ARM_REG_R0) if kind in ('select','mode','get') else None
   results.append((returned,calls,writes,bytes(u.mem_read(ctx+8,2)) if kind=='select' else None,u.mem_read(flag,1) if kind=='release' else None))
  assert results[0]==results[1],(name,results)
  print('PASS',name,results[0][:3])
