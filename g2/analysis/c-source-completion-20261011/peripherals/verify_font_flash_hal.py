"""Bounded actual C/native flash HAL comparisons with selected external calls cut."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CHILDREN={'g2_gpio_critical_save':0x473940,'audio_delay_us_selected':0x4807a0,
          'audio_uart_pin_mux_enable':0x4c44bc,'audio_uart_pin_mux_disable':0x4c4530,
          'audio_uart_mux_bit_get':0x4c37a8}
FUNCTIONS={'transition':('audio_uart_font_mspi_transition',0x4c0758),
           'suspend':('audio_uart_font_mspi_suspend',0x4bfd44),
           'resume':('audio_uart_font_mspi_resume',0x4bfd62),
           'prepare':('audio_uart_font_power_prepare',0x4c235c),
           'pins':('audio_uart_font_pin_mux_disable',0x4c45a4)}
with tempfile.TemporaryDirectory() as td:
 shim=Path(td)/'shim.c'
 shim.write_text(''.join('__attribute__((naked,used)) void '+n+'(void){__asm__ volatile("movs r0, #0\\n bx lr");}\n' for n in CHILDREN))
 elf=Path(td)/'hal.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_mspi_transition',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_flash_hal.c'),str(shim),'-o',str(elf)],check=True)
 syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 def run(candidate,kind,variant):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
  u.mem_map(0x100000,0x100000)
  for v,d in segs:u.mem_write(v,d)
  u.mem_map(0x20000000,0x100000);u.mem_map(0x40000000,0x10000);u.mem_map(0x40060000,0x10000)
  D=0x20010000;Q=0x20011000;R=0x20012000
  u.mem_write(D,b'\0'*0x900);u.mem_write(Q,b'\0'*0x100);u.mem_write(R,b'\0'*0x100)
  u.mem_write(D,struct.pack('<I',0x01bebebe if variant!='invalid' else 0x1234))
  u.mem_write(D+4,struct.pack('<I',1));u.mem_write(D+0x828,struct.pack('<I',Q))
  u.mem_write(Q,struct.pack('<I',0x01cdcdcd | (0x02000000 if kind=='resume' else 0)))
  u.mem_write(Q+0x24,struct.pack('<I',R));u.mem_write(R,struct.pack('<I',0x40060000))
  u.mem_write(0x40060000,struct.pack('<I',3))
  u.mem_write(0x40060200+0x1000,struct.pack('<I',0xffff1234))
  u.mem_write(0x40004110,struct.pack('<I',0xa5a55a5a))
  args={'transition':(1,variant=='enable',1,8),'suspend':(D,0,0,0),
        'resume':(D,0,0,0),'prepare':(D,0x1fff,0,0),'pins':(21,0,0,0)}[kind]
  for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,int(val))
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  def bypass(uc,address,size,_):
   if size==4 and bytes(uc.mem_read(address,4))[1:]==b'\xf3\x10\x88':
    uc.reg_write(UC_ARM_REG_PC,(address+4)|1)
   elif not candidate and address in CHILDREN.values():
    uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,bypass)
  name,stock=FUNCTIONS[kind]
  try:u.emu_start((syms[name] if candidate else stock)|1,0x600000,count=10000)
  except Exception:
   pc=u.reg_read(UC_ARM_REG_PC);print('oracle stop',candidate,kind,variant,hex(pc),bytes(u.mem_read(pc,4)).hex())
   raise
  return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(D,0x900)),bytes(u.mem_read(Q,0x100)),
          bytes(u.mem_read(0x40000000,0x10000)),bytes(u.mem_read(0x40060000,0x2000)))
 for kind,variant in [('transition','enable'),('transition','disable'),('suspend','valid'),
                      ('resume','valid'),('prepare','valid'),('prepare','invalid'),
                      ('pins','valid'),('pins','invalid')]:
  left=run(False,kind,variant);right=run(True,kind,variant)
  if kind=='transition':left=left[1:];right=right[1:]
  assert left==right,(kind,variant,left[0],right[0])
  print('PASS flash HAL',kind,variant)
