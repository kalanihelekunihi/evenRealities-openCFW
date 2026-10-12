from pathlib import Path
import tempfile,subprocess,struct,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-cache-getter-round87/cache_entry_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,const char*e,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cache_info',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for entry,offset in [(0,0)]+[(0x20005000,x) for x in [0,1,8,16,0x7fffffff,0x80000000,0xffffffff]]:
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20005008,struct.pack('<I',offset));calls=[];faults=[];log=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1
   def readstr(ptr):
    out=bytearray()
    for j in range(512):
     v=bytes(u.mem_read(ptr+j,1))
     if v==b'\0':return out.decode()
     out+=v
    raise AssertionError('unterminated')
   def hook(uc,a,size,user):
    if a!=log:return
    r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];stack=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));calls.append((r[0],readstr(r[1]),r[2],readstr(r[3]),*[readstr(v) for v in stack]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,address,size,value,user):faults.append((address,size,value));return False
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_R0,entry);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   try:u.emu_start((syms['audio_uart_font_cache_info'] if isc else 0x4d5396)|1,0x600000,count=1000)
   except UcError:assert faults==[(0xffffffff,4,0)],faults
   outputs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(entry,offset,outputs);count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_GETTER_ASSERT_AND_OFFSET','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Logger cut and first unmapped assertion store; other accessor bodies not newly qualified.','Full image layout/byte equality/hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
