"""Actual compiled-C/stock MX25U power guard comparisons; hardware branches remain unqualified."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
NAMES=['audio_power_peripheral_on','audio_power_peripheral_off','audio_uart_pin_mux_enable','audio_uart_font_pin_mux_disable','audio_uart_font_mspi_transition','audio_uart_font_mspi_suspend','audio_uart_font_mspi_resume','audio_uart_font_power_prepare','audio_delay_us_selected']
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c';shim.write_text(''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("movs r0, #0\\n bx lr");}\n' for n in NAMES))
 elf=Path(td)/'power.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_flash_power',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_flash_power.c'),str(shim),'-o',str(elf)],check=True)
 syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,case):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x40060000,0x10000)
  u.mem_map(0x20000000,0x100000);D=0x20010000;u.mem_write(D,b'\0'*0x900)
  if case!='null':u.mem_write(D,struct.pack('<I',0x01bebebe if case!='badmagic' else 0x1234))
  mode={'null':0,'badmagic':0,'badmode':3,'busy1':1,'busy2':2,'norestore':0,'restore':0}[case]
  if case=='busy1':u.mem_write(D+0x840,struct.pack('<I',1))
  if case=='busy2':u.mem_write(D+0x20,struct.pack('<I',1))
  if case=='restore':
   u.mem_write(D+0x860,b'\1');u.mem_write(D+0x8c9,b'\4')
   for off in range(0x864,0x8c8,4):u.mem_write(D+off,struct.pack('<I',0xa5a50000|off))
   u.mem_write(D+0x8b8,struct.pack('<I',0x11223344))
   u.mem_write(D+0x8a0,struct.pack('<I',0x2200))
  if not candidate:
   children={0x47f5b8,0x47f7ae,0x4c44bc,0x4c45a4,0x4c0758,0x4bfd44,0x4bfd62,0x4c235c,0x4807a0}
   def bypass(uc,address,size,_):
    if address in children:
     uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,bypass)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.reg_write(UC_ARM_REG_R0,0 if case=='null' else D);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,1)
  try:u.emu_start((syms['audio_uart_font_flash_power'] if candidate else 0x4c26e0)|1,0x600000,count=10000)
  except Exception:
   print('oracle stop',candidate,case,hex(u.reg_read(UC_ARM_REG_PC)))
   raise
  return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(D,0x900)),bytes(u.mem_read(0x40060000,0x300))
 for case in ('null','badmagic','badmode','busy1','busy2','norestore','restore'):
  a=run(False,case);b=run(True,case);assert a==b,(case,a[0],b[0]);print('PASS flash guard',case)
