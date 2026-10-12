"""Full cached-read body comparison; child operations are explicit cuts."""
from pathlib import Path
import subprocess,tempfile,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED,UcError
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent/'root-fs-cached-round64/cached_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void *audio_uart_lv_grid_copy_454738(void*a,const void*b,unsigned c){return a;} void *audio_uart_lv_malloc(unsigned n){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_fs_read_cached_4c713c',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 # start,end,position,request,cache_size,buffer_present,allocator_success
 paths=[(10,19,12,n,cap,1,1) for n in [0,1,8,9,16,65546] for cap in [4,16,65536,0xffffffff]]
 paths += [(10,19,pos,n,cap,buf,alloc) for pos in [0,20] for n in [0,4,16] for cap in [4,16] for buf in [0,1] for alloc in [0,1]]
 count=0
 for path,childcount,result,mutation in itertools.product(paths,[0,1,7,16,65536],[0,1,256,0x87654321],[0,1]):
  outputs=[]
  for isc in [False,True]:
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   f=0x20003000;drv=0x20004000;cache=0x20005000;buffer=0x20010000;out=0x20030000;br=0x20006000;read=0x600100;seek=0x600200
   def put(a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
   def word(a):return int.from_bytes(u.mem_read(a,4),'little')
   def string(a):
    data=bytearray()
    while (v:=bytes(u.mem_read(a+len(data),1)))!=b'\0':data.extend(v)
    return data.decode()
   start,end,pos,request,cap,present,alloc=path
   put(f,0x20007000);put(f+4,drv);put(f+8,cache);put(drv+4,cap);put(drv+20,read|1);put(drv+28,seek|1)
   for off,val in [(0,start),(4,end),(8,pos),(12,buffer if present else 0)]:put(cache+off,val)
   put(br,0);calls=[];faults=[]
   cuts={(syms[n] if isc else a)&~1:k for n,a,k in [('audio_uart_lv_grid_copy_454738',0x454738,'copy'),('audio_uart_lv_malloc',0x44f718,'malloc'),('audio_uart_lvgl_log',0x44d25c,'log')]};cuts[read]='read';cuts[seek]='seek'
   def hook(uc,a,size,user):
    if a not in cuts:return
    kind=cuts[a];args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=0
    if kind=='copy':calls.append((kind,*args[:3]));ret=args[0]
    elif kind=='malloc':calls.append((kind,args[0]));ret=buffer if alloc else 0
    elif kind=='seek':calls.append((kind,*args));ret=0xffffffff
    elif kind=='read':
     dest=word(uc.reg_read(UC_ARM_REG_SP));calls.append((kind,*args,word(dest)));put(dest,childcount);ret=result
     if mutation:put(cache+4,33);put(cache+8,99)
    else:
     sp=uc.reg_read(UC_ARM_REG_SP);calls.append((kind,args[0],string(args[1]),args[2],string(args[3]),string(word(sp)),string(word(sp+4)),string(word(sp+8))))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,a,size,value,user):faults.append((a,size,value));return False
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,v in [(UC_ARM_REG_R0,f),(UC_ARM_REG_R1,out),(UC_ARM_REG_R2,request),(UC_ARM_REG_R3,br)]:u.reg_write(reg,v)
   try:u.emu_start((syms['audio_uart_lv_fs_read_cached_4c713c'] if isc else 0x4c713c)|1,0x600000,count=10000)
   except UcError:
    assert faults and faults[0][0]==0xffffffff
   outputs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),word(br),bytes(u.mem_read(cache,16)),None if faults else u.reg_read(UC_ARM_REG_SP)))
  assert outputs[0]==outputs[1],(path,childcount,result,mutation,outputs);count+=1
 r={'status':'PASS_BOUNDED_COMPILED_ARM_NATIVE_CACHED_READ','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'native_payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Copy, allocator, logger and indirect read/seek are controlled cuts; copy checks arguments rather than copied bytes.','Includes cache hit, split refill/direct read, outside-cache refill/direct read, memory-mapped limit, 16-bit partial length, read mutations, status truncation and allocation failure.','Allocation failure stops at first native fault store; image layout, byte equality and hardware unproven.']};(SRC.parent/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
