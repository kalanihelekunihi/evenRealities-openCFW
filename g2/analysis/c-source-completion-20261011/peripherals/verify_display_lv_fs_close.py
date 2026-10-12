"""Native/compiled ARM filesystem close, including post-callback reloads."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
SRC=Path(__file__).parent/'root-fs-close-round59/fs_close_candidate.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_heap_free(void*p){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_file_close_4c6ee0',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for present,callback,cache_size,cache,buffer,result,mutation in itertools.product([0,1],[0,1],[0,1,0xffffffff],[0,1],[0,1],[0,255,256,0x87654321],[0,1,2]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   file=0x20003000;driver=0x20004000;cached=0x20005000;cb=0x600100;free=(syms['audio_uart_lv_heap_free'] if isc else 0x44f758)&~1
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   put(file,0x20006000);put(file+4,driver if present else 0);put(file+8,cached if cache else 0);put(driver+4,cache_size);put(driver+16,cb|1 if callback else 0);put(cached+12,0x20007000 if buffer else 0)
   put(driver+0x104,1);put(cached+0x10c,0x20007100);calls=[]
   def hook(uc,address,size,user):
    if address==cb:
     calls.append(('callback',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     if mutation==1:put(file+4,driver+0x100);put(file+8,cached+0x100)
     if mutation==2:put(driver+4,0)
     uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif address==free:
     calls.append(('free',uc.reg_read(UC_ARM_REG_R0)))
     if mutation==1:put(file+8,cached+0x180)
     uc.reg_write(UC_ARM_REG_R0,0xaabbccdd);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,file)
   u.emu_start((syms['audio_uart_lv_fs_file_close_4c6ee0'] if isc else 0x4c6ee0)|1,0x600000,count=10000)
   outputs.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(file,12)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(present,callback,cache_size,cache,buffer,result,mutation,outputs)
  count+=1
 receipt={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_FS_CLOSE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Controlled callback and heap-free cuts prove bounded ordering, reloads, return truncation and field resets.','Indirect callback installation and runtime, full image layout and hardware remain separate gates.']}
 (SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
