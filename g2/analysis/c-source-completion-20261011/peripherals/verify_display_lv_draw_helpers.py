from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-draw-helpers-round68/helpers_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_area_width_451598',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 values=[0,1,65535,65536,0x7fffffff,0x80000000,0xffffffff];count=0
 for name,native in [('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_draw_buf_set_flag_48b750',0x48b750)]:
  for first,second in itertools.product(values,values):
   outputs=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    obj=0x20003000;u.mem_write(obj,first.to_bytes(4,'little')+b'\xa5'*4+second.to_bytes(4,'little')+b'\xff'*4);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,second);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000);outputs.append((u.reg_read(UC_ARM_REG_R0) if native==0x451598 else None,bytes(u.mem_read(obj,16)),u.reg_read(UC_ARM_REG_SP)))
   assert outputs[0]==outputs[1],(name,first,second,outputs);count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_HELPERS','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Boundary values check unsigned width wrapping and flag truncation; full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
