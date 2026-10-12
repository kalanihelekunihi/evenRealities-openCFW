from pathlib import Path
import subprocess,tempfile,json,hashlib
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_children.c'
with tempfile.TemporaryDirectory() as td:
 td=Path(td);shim=td/'shim.c';shim.write_text('unsigned char audio_uart_display_lv_root[512]; void *audio_uart_lv_malloc(unsigned n){(void)n;return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){(void)a;(void)b;(void)c;(void)d;}')
 elf=td/'span.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-fno-builtin','-ffunction-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_span_stack_init_4c6d04',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as fp:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(fp).iter_segments() if s['p_type']=='PT_LOAD']
 count=0
 for allocated in [0,1,0x20002000,0xffffffff]:
  for pattern in [0,0xa5,0xff]:
   outputs=[]
   for isc in [False,True]:
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    root=syms['audio_uart_display_lv_root'] if isc else 0x2006f548;u.mem_write(root,bytes([pattern])*512);calls=[];faults=[]
    malloc=(syms['audio_uart_lv_malloc'] if isc else 0x44f718)&~1;log=(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1
    def string(uc,a):
     out=bytearray()
     while True:
      x=bytes(uc.mem_read(a+len(out),1))
      if x==b'\x00':return out.decode('ascii')
      out.extend(x);assert len(out)<300
    def hook(uc,address,size,user):
     if address==malloc:
      calls.append(('allocate',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,allocated);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     elif address==log:
      sp=uc.reg_read(UC_ARM_REG_SP);args=[uc.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]+[int.from_bytes(uc.mem_read(sp+i*4,4),'little') for i in range(3)]
      calls.append(('log',args[0],string(uc,args[1]),args[2],string(uc,args[3]),*[string(uc,a) for a in args[4:]],bytes(uc.mem_read(root+452,4))));uc.reg_write(UC_ARM_REG_R0,0x12345678);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def fault(uc,access,address,size,value,user):
     faults.append((address,size,value));return False
    u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg in [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]:u.reg_write(reg,0xabcdef00+reg)
    try:u.emu_start((syms['audio_uart_lv_span_stack_init_4c6d04'] if isc else 0x4c6d04)|1,0x600000,count=1000)
    except UcError:assert faults
    outputs.append((calls,bytes(u.mem_read(root,512)),faults,u.reg_read(UC_ARM_REG_SP) if allocated else None))
   assert outputs[0]==outputs[1],(allocated,pattern,outputs)
   assert outputs[0][0][0]==('allocate',1796)
   assert outputs[0][2]==([(0xffffffff,4,0)] if allocated==0 else [])
   count+=1
 r={'status':'PASS_COMPILED_ARM_NATIVE_SPAN_STACK_INITIALIZER','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'limits':['Allocator and logger are controlled child cuts.','Failure comparison stops at the first native faulting write; physical fault handling is unverified.','Void-return scratch registers and full Main image are not qualified.']}
 (Path(__file__).parent/'root-main-init-round55/span-stack-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
