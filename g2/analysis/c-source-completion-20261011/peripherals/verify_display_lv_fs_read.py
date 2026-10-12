from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-fs-read-round63/read_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_fs_read_cached_4c713c(void*a,void*b,unsigned c,unsigned*d){return 0;}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_file_read_4c6f46',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for present,cache,read,seek,out,result,childcount in itertools.product([0,1],[0,1,0xffffffff],[0,1],[0,1],[0,1],[0,1,256,0x87654321],[0,12,0xffffffff]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   file=0x20003000;driver=0x20004000;buffer=0x20005000;readout=0x20006000;cb=0x600100;cached=(syms['audio_uart_lv_fs_read_cached_4c713c'] if isc else 0x4c713c)&~1
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   put(file,0x20007000);put(file+4,driver if present else 0);put(driver+4,cache);put(driver+20,cb|1 if read else 0);put(driver+28,0x600201 if seek else 0);put(readout,0xaabbccdd);calls=[]
   def hook(uc,a,size,user):
    if a not in [cb,cached]:return
    args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if a==cb:dest=word(uc.reg_read(UC_ARM_REG_SP));calls.append(('callback',*args,word(dest)))
    else:dest=args[3];calls.append(('cached',*args[:3],word(dest)))
    put(dest,childcount);put(file,0x20007100);uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in [(UC_ARM_REG_R0,file),(UC_ARM_REG_R1,buffer),(UC_ARM_REG_R2,12),(UC_ARM_REG_R3,readout if out else 0)]:u.reg_write(reg,v)
   u.emu_start((syms['audio_uart_lv_fs_file_read_4c6f46'] if isc else 0x4c6f46)|1,0x600000,count=10000);outputs.append((calls,u.reg_read(UC_ARM_REG_R0),word(readout),bytes(u.mem_read(file,12)),u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(present,cache,read,seek,out,result,childcount,outputs);count+=1
 receipt={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_FS_READ','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Cached-read child and indirect read callback are controlled cuts; cached-read remains a genuine production import.','Covers missing driver/read/seek, null output, zeroed local count, callback stack ABI, returned counts and byte status truncation.','Native layout, byte equality and hardware remain unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
