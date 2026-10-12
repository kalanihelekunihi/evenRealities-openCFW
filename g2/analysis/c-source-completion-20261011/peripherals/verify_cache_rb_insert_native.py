from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-rb-insert-round111';SRC=DIR/'rb_insert_candidate.c';CORE=ROOT/'components/audio/uart_thread_source_candidate/display_font_rb_core.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
T,N,NEW,D,K=0x20001000,0x20002000,0x20002200,0x20003000,0x20004000;CB,CB2=0x600100,0x600104;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_rb_alloc_insert',0x5c34e4),('audio_uart_lv_cache_rb_create_node_5c37a4',0x5c37a4),('audio_uart_lv_cache_rb_find_parent_5c3838',0x5c3838)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_lv_heap_alloc(unsigned n){return 0;} void audio_uart_font_rb_fix_insert(void*a,void*b){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(SRC),str(CORE),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={CB:'compare',CB2:'compare2'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('alloc','audio_uart_lv_heap_alloc',0x44f730),('fix','audio_uart_font_rb_fix_insert',0x5c38cc),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,shape=2,order=1,node_alloc=NEW,data_alloc=D+256,node_size=44,mutate=0):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   u.mem_write(T,W(N if shape else 0,CB|1,node_size));u.mem_write(N,bytes([0xa5])*768);u.mem_write(D,bytes([0xa5])*512);u.mem_write(NEW,W(0,0,0,0,K))
   for i in range(3):u.mem_write(N+64*i,W(0 if i==0 else N,N+64 if i==0 and shape==2 else 0,N+128 if i==0 and shape==2 else 0,1 if i==0 else 0,D+64*i))
   calls=[];faults=[];allocations=0
   def hook(uc,addr,size,user):
    nonlocal allocations
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
    if op.startswith('compare'):
     calls.append((op,*r[:2]));ret=order
     if mutate:uc.mem_write(T+4,W(CB2|1));uc.mem_write(NEW+16,W(K+4));uc.mem_write(NEW+12,bytes([0xff]))
    elif op=='alloc':
     calls.append((op,r[0]));ret=node_alloc if allocations==0 else data_alloc;allocations+=1
     if ret==NEW:uc.mem_write(NEW,bytes([0xa5])*20)
     if mutate and allocations==1:uc.mem_write(T+8,W(64))
    elif op=='fix':
     calls.append((op,*r[:2],bytes(uc.mem_read(NEW,20)).hex(),bytes(uc.mem_read(T,12)).hex()))
     if mutate:uc.mem_write(NEW+16,W(0x12345678));uc.mem_write(NEW+12,bytes([1]))
    else:
     fmt,expr,msg=struct.unpack('<III',uc.mem_read(sp,12));calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr),string(uc,msg)))
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=10000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,12)),bytes(u.mem_read(N,768)),bytes(u.mem_read(D,512))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,shape,hex(order),node_alloc,data_alloc,node_size,mutate,outs);counts[s]+=1
 orders=[0,1,127,128,255,256,257,0xffffffff,0x7fffffff,0x80000000]
 for shape,order,node,data,mutate in itertools.product(range(3),orders,[0,NEW],[0,D+256],[0,1,2]):check(0,[T,K],shape,order,node,data,mutate=mutate)
 check(0,[0,K])
 for node,data,size,mutate in itertools.product([0,NEW],[0,D+256],[0,1,44,0xffffffff],[0,1,2]):check(1,[T],node_alloc=node,data_alloc=data,node_size=size,mutate=mutate)
 for shape,order,mutate in itertools.product(range(3),orders,[0,1,2]):check(2,[T,NEW],shape,order,mutate=mutate)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_RB_INSERT_NODE_PARENT','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'selected_core_sha256':hashlib.sha256(CORE.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual RB find/node-create/parent-walk execute; allocator/comparator/balancing/logger controlled child cuts.','Full signed parent/final compare versus signed low-byte find behavior,current comparator,key lifetime through balance,allocation failures,mutation and native fatal stores compared.','Concrete balancing/removal/heap/data/connected cache and full-image/layout/byte equality/hardware open.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
