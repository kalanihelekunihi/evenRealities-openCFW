from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/handlers_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callbacks=['audio_uart_lv_draw_buf_malloc_cb_48b80c','audio_uart_lv_draw_buf_free_cb_48b816','audio_uart_lv_draw_buf_align_cb_48b81e','audio_uart_lv_draw_width_stride_cb_48b82a']
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_draw_memzero_48aa54(void*a,unsigned b){}'+' '.join('void '+n+'(void){}' for n in callbacks));elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_draw_handlers_default_48aa80',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for default in [False,True]:
  for pattern in [0,0xa5,0xff]:
   for values in [[0]*6,[0xffffffff]*6,[1,2,3,4,5,6]]:
    outputs=[]
    for isc in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in segs:u.mem_write(a,d)
     obj=0x20003000;sp=0x200ff000;u.mem_write(obj,bytes([pattern])*40);calls=[];cut=(syms['audio_uart_lv_draw_memzero_48aa54'] if isc else 0x48aa54)&~1
     def hook(uc,a,size,user):
      if a!=cut:return
      ptr=uc.reg_read(UC_ARM_REG_R0);length=uc.reg_read(UC_ARM_REG_R1);calls.append((ptr,length));u.mem_write(ptr,bytes(length));uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
     for reg,val in zip([UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],values):u.reg_write(reg,val)
     for off,val in enumerate(values[3:]):u.mem_write(sp+4*off,val.to_bytes(4,'little'))
     name,native=('audio_uart_lv_draw_handlers_default_48aa80',0x48aa80) if default else ('audio_uart_lv_draw_handlers_init_48aaa2',0x48aaa2);u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000)
     raw=bytearray(u.mem_read(obj,40))
     if default and isc:
      for off,name,ptr in [(0,callbacks[0],0x48b80d),(4,callbacks[1],0x48b817),(8,callbacks[2],0x48b81f),(20,callbacks[3],0x48b82b)]:
       assert int.from_bytes(raw[off:off+4],'little')==(syms[name]|1);raw[off:off+4]=ptr.to_bytes(4,'little')
     outputs.append((calls,bytes(raw),u.reg_read(UC_ARM_REG_SP)))
    assert outputs[0]==outputs[1],(default,pattern,values,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_HANDLERS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Zero child cut; verifies32-byte clear, six saved callback words and default callback identities.','Void scratch R0 not compared; callback bodies qualified separately, image layout/byte equality/hardware unproven.']};(SRC.parent/'handlers-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
