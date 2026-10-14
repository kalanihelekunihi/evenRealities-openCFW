#!/usr/bin/env python3
"""Compare Apollo display buffer unlock C and native helper calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP,UC_ARM_REG_IPSR
source=Path(__file__).with_name('display_buffer_unlock.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 d=Path(d);a=d/'stubs.s'
 names=['audio_uart_lvgl_log','xQueueGiveFromISR','audio_uart_queue_send']
 a.write_text('.syntax unified\n.thumb\n.text\n'+''.join(f'.global {n}\n.thumb_func\n{n}:\n bx lr\n' for n in names))
 image=d/'unlock.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2',
  '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,display_driver_case3_sync',str(source),str(a),'-o',str(image)],
  check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
  cell=next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='display_buffer_semaphore')
  assert cell['st_size']==4 and elf.get_section(cell['st_shndx']).name=='.bss'
 for handle in (0,0x20001234):
  for ipsr in (0,16):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    slot=syms['display_buffer_semaphore'] if compiled else 0x200746bc
    cpu.mem_write(slot,handle.to_bytes(4,'little'))
    targets={((syms[n] if compiled else native)&~1):label for n,native,label in [
      ('audio_uart_lvgl_log',0x44d25c,'log'),('xQueueGiveFromISR',0x441a42,'give_isr'),
      ('audio_uart_queue_send',0x4417ee,'send_task')]}
    calls=[]
    def cs(u,p):return bytes(u.mem_read(p,200)).split(b'\0')[0].decode('ascii')
    def hook(u,address,_size,_user):
     label=targets.get(address)
     if label is None:return
     r0=u.reg_read(UC_ARM_REG_R0);r1=u.reg_read(UC_ARM_REG_R1)
     if label=='log':
      assert r0==3 and u.reg_read(UC_ARM_REG_R2)==0x131
      assert cs(u,r1)==r'D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\lvgl_ambiq_porting\lv_ambiq_display.c'
      assert cs(u,u.reg_read(UC_ARM_REG_R3))=='display_buffer_unlock'
      assert cs(u,int.from_bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4),'little'))=='display buffer semaphore is not initialized!\n'
     elif label=='give_isr':assert (r0,r1)==(handle,0)
     elif label=='send_task':assert (r0,r1,u.reg_read(UC_ARM_REG_R2),u.reg_read(UC_ARM_REG_R3))==(handle,0,0,0)
     calls.append(label)
     u.reg_write(UC_ARM_REG_R0,1)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    cpu.hook_add(UC_HOOK_CODE,hook)
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    cpu.reg_write(UC_ARM_REG_IPSR,ipsr)
    cpu.emu_start((syms['display_driver_case3_sync'] if compiled else 0x47386a)|1,0x600000,count=200)
    observations.append(calls)
   assert observations[0]==observations[1],(handle,ipsr,observations)
print('PASS_DISPLAY_BUFFER_UNLOCK_NATIVE',4)
