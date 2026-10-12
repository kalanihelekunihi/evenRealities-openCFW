from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-bin-open-round65/data_get_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_heap_alloc(unsigned n){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_bin_decoder_data_get_4c81a2',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for owner,alloc,pattern,mutate in itertools.product([0,0x20007000],[0,0x20008000],[0,0xa5],[False,True]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   dsc=0x20003000;u.mem_write(dsc,bytes([pattern])*80)
   def put(a,v):u.mem_write(a,v.to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def string(a):
    data=bytearray()
    while (v:=bytes(u.mem_read(a+len(data),1)))!=b'\0':data.extend(v)
    return data.decode()
   put(dsc+72,owner);calls=[];faults=[];alloccut=(syms['audio_uart_lv_heap_alloc'] if isc else 0x44f730)&~1;logcut=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1
   def hook(uc,a,size,user):
    if a==alloccut:
     calls.append(('alloc',uc.reg_read(UC_ARM_REG_R0)))
     if mutate:put(dsc+72,0x20009000)
     uc.reg_write(UC_ARM_REG_R0,alloc);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    elif a==logcut:
     args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);calls.append(('log',args[0],string(args[1]),args[2],string(args[3]),*[string(word(sp+i)) for i in [0,4,8]]));uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,a,size,value,user):faults.append((a,size,value));return False
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,dsc)
   try:u.emu_start((syms['audio_uart_lv_bin_decoder_data_get_4c81a2'] if isc else 0x4c81a2)|1,0x600000,count=10000)
   except UcError:assert faults and faults[0][0]==0xffffffff
   outputs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(dsc,80)),None if faults else u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(owner,alloc,pattern,mutate,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_DATA_GET','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Zeroed allocator and logger are controlled cuts; allocator68-byte contract and fresh owner store compared.','Fatal allocation failure stops at first fault; full image and hardware remain unproven.']};(SRC.parent/'data-get-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
