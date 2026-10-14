#!/usr/bin/env python3
"""Compare four display-driver wrappers with authenticated Apollo native calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
source=Path(__file__).with_name('display_driver_aux.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
functions=[('display_driver_init_473abc',0x473abc,'audio_uart_ring_state_transition_4c9b86',0x4c9b86,(12,)),
 ('display_driver_init_473ac6',0x473ac6,'audio_uart_ring_resource_transition_4c9be2',0x4c9be2,(12,)),
 ('display_driver_case1_b',0x473b34,'osTimerStart',0x449498,None),
 ('display_driver_case5_a',0x473b46,'audio_timer_stop',0x4494d8,None)]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(
  f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in [x[2] for x in functions])+
  '')
 elfpath=d/'aux.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
  '-Wl,-Ttext=0x100000','-Wl,-e,display_driver_init_473abc',str(source),str(a),'-o',str(elfpath)],
  check=True,capture_output=True)
 with elfpath.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
  syms={s.name:s['st_value'] for s in symbols}
  timer_cell=next(s for s in symbols if s.name=='display_driver_timer_handle')
  assert timer_cell['st_size']==4 and elf.get_section(timer_cell['st_shndx']).name=='.bss'
 for name,native,helper,native_helper,_ in functions:
  for handle in (0,0x20001234):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000)
    cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    slot=syms['display_driver_timer_handle'] if compiled else 0x200744f0
    cpu.mem_write(slot,handle.to_bytes(4,'little'))
    target=(syms[helper] if compiled else native_helper)&~1
    calls=[]
    def hook(uc,address,_size,_user):
     if address==target:
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
      expected=(12,) if helper.startswith('audio_uart_ring_') else ((handle,2000) if helper=='osTimerStart' else (handle,))
      got=(r0,r1)[:len(expected)]
      assert got==expected,(name,compiled,handle,got,expected)
      calls.append(got)
      uc.reg_write(UC_ARM_REG_R0,0x12345678)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.emu_start((syms[name] if compiled else native)|1,0x600000,count=100)
    observations.append(calls)
   assert observations[0]==observations[1] and len(observations[0])==1,(name,handle,observations)
print('PASS_DISPLAY_DRIVER_AUX_NATIVE',len(functions)*2)
