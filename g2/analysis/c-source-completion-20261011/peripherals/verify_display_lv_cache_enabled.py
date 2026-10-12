from pathlib import Path
import subprocess,tempfile,json,hashlib,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-cache-enabled-round76/cache_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 elf=Path(tmp)/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_image_cache_enabled_4d4b24',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for name,native in [('audio_uart_lv_cache_enabled_4d5104',0x4d5104),('audio_uart_lv_image_cache_enabled_4d4b24',0x4d4b24)]:
  for capacity in [0,1,2,255,256,0x7fffffff,0x80000000,0xffffffff]:
   out=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    u.mem_write(0x20001000,struct.pack('<III',0xdeadbeef,0xffffffff,capacity));u.mem_write(0x2006f548+0x134,struct.pack('<I',0x20001000));u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.emu_start((syms[name] if isc else native)|1,0x600000,count=1000);out.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP)))
   assert out[0]==out[1],(name,capacity,out);count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_CAPACITY','cases':count,'child_cuts':0,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Valid cache-pointer contract; native has no null guard.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
