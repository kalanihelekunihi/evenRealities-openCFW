from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-cache-create-core-round102/cache_create_core_candidate.c';MUTEX=ROOT/'components/audio/uart_thread_source_candidate/display_lv_init_mutex_children.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,V=0x20001000,0x20002000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
callbacks={'alloc':0x600100,'init':0x600104,'init2':0x600108}
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_mutex_ensure(unsigned*a){} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_cache_create_4d4cd4',str(SRC),str(MUTEX),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={a:op for op,a in callbacks.items()};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('ensure','audio_uart_lv_mutex_ensure',0x4d47cc),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 count=0
 for allocated,result,node_size,capacity,ops,mutate in itertools.product([False,True],[0,1,0x100,0xffffffff],[0,12,0xffffffff],[0,32,0xffffffff],[(0,0,0),(0x12345678,0x87654321,0xffffffff)],[0,1,2]):
  outs=[]
  for u,cuts,isc in engines:
   u.mem_write(C,bytes([0xa5])*68);u.mem_write(V,W(callbacks['alloc']|1,callbacks['init']|1));u.mem_write(0x200ff000,W(ops[1],ops[2]));calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
    if op=='alloc':
     calls.append((op,));ret=C if allocated else 0
     if mutate:uc.mem_write(V+4,W(callbacks['init2']|1))
    elif op.startswith('init'):
     calls.append((op,r[0],bytes(uc.mem_read(C,28)).hex()));assert r[0]==C;ret=result
     if mutate==2:uc.mem_write(C+12,W(0x12345678));uc.mem_write(C+28,W(0,0xabcdef01))
    elif op=='ensure':
     calls.append((op,r[0]));assert r[0]==C+28;uc.mem_write(C+28,W(1,0x87654321));ret=0xdeadbeef
    elif op=='free':calls.append((op,r[0]));assert r[0]==C
    else:
     fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
     if r[2]==51:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
     else:assert r[2]==60
     calls.append(item)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[V,node_size,capacity,ops[0]]):u.reg_write(reg,value)
   try:u.emu_start((syms['audio_uart_lv_cache_create_4d4cd4'] if isc else 0x4d4cd4)|1,0x600000,count=2000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,68)),bytes(u.mem_read(V,8))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(allocated,result,node_size,capacity,ops,mutate,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_CREATE_CORE','cases':count,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'mutex_wrapper_sha256':hashlib.sha256(MUTEX.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_range':'4d4cd4..4d4d6a','limits':['Six argument words implement native12-byte by-value ops ABI (R3 plus two stack words). Actual mutex wrapper executes; allocator/class-init/ensure/free/logger child cuts.','Font convenience wrappers in candidate not newly qualified. Concrete class/heap/placement/full-image/hardware gates remain open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
