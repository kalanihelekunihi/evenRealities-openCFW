from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-image-cache-startup-round104/lru_init_candidate.c';ARRAY=ROOT/'components/audio/uart_thread_source_candidate/display_lv_global_init.c'
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_initialize',0x5c2c54),('audio_uart_lv_cache_size_lru_init_5c2d30',0x5c2d30),('audio_uart_lv_cache_count_data_size_5c330c',0x5c330c),('audio_uart_lv_cache_size_data_size_5c3310',0x5c3310)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_font_rb_initialize(void*a,unsigned b,unsigned c){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(SRC),str(ARRAY),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms[s] if isc else n)&~1:op for op,s,n in [('rb','audio_uart_font_rb_initialize',0x5c3428),('log','audio_uart_lvgl_log',0x44d25c)]};engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,node=24,compare=0x12345679,free=0x87654321,result=1,mutate=0):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   words=[0xa5a5a5a5]*17;words[0]=node if idx>=2 else words[0];words[1]=node;words[4]=compare;words[6]=free;u.mem_write(C,W(*words));calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
    if op=='rb':
     calls.append((op,*r[:3]));uc.mem_write(C+40,W(0,r[1],r[2]))
     if mutate:uc.mem_write(C+4,W(0xdeadbeef));uc.mem_write(C+52,W(1,2,3));uc.mem_write(C+64,W(0xabcdef01))
     ret=result
    else:
     fmt,expr=struct.unpack('<II',uc.mem_read(sp,8));item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr))
     if r[2] not in [206,229]:item+=(string(uc,struct.unpack('<I',uc.mem_read(sp+8,4))[0]),)
     calls.append(item);ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,C)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=2000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   mem=list(struct.unpack('<17I',u.mem_read(C,68)))
   if idx<2 and not faults and result!=0:
    pointer=(syms[providers[2+idx][0]]|1) if isc else (0x5c330d if idx==0 else 0x5c3311)
    assert mem[16]==pointer,(s,isc,hex(mem[16]),hex(pointer));mem[16]='count_size' if idx==0 else 'data_size'
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),mem));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,node,compare,free,result,mutate,outs);counts[s]+=1
 for idx,node,compare,free,result,mutate in itertools.product(range(2),[0,1,4,24,0xffffffeb,0xffffffec,0xffffffff],[0,0x12345679],[0,0x87654321],[0,1,0x100,0xffffffff],[0,1]):check(idx,node,compare,free,result,mutate)
 for idx,value in itertools.product([2,3],[0,1,24,0x7fffffff,0x80000000,0xffffffff]):
  check(idx,node=value)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_COUNT_SIZE_LRU_INITIALIZERS','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual array initializer executes; tree init and logger controlled child cuts, including full-word returns and mutation.','Native wrapped node-size arithmetic and fatal store exact; data size leaf varied word0. Concrete RB/class/allocator/image/full-image/hardware gates open.']};(SRC.parent/'lru-init-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
