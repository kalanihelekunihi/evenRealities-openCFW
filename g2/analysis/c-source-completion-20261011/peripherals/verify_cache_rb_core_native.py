from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-cache-rb-core-round105/cache_rb_core_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
T,N,D,K=0x20001000,0x20002000,0x20003000,0x20004000;CB,CB2=0x600100,0x600104;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_rb_initialize',0x5c3428),('audio_uart_font_rb_find',0x5c3594),('audio_uart_font_rb_clear',0x5c3716),('audio_uart_font_rb_erase',0x5c36c8),('audio_uart_lv_cache_rb_memzero_5c341c',0x5c341c)]
shapes=[[],[(-1,-1,-1)],[(-1,1,2),(0,-1,-1),(0,-1,-1)],[(-1,1,-1),(0,2,-1),(1,-1,-1)],[(-1,-1,1),(0,-1,2),(1,-1,-1)],[(-1,1,2),(0,3,4),(0,5,6),(1,-1,-1),(1,-1,-1),(2,-1,-1),(2,-1,-1)]]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){} void audio_uart_lv_heap_free(void*a){} void*audio_uart_font_rb_remove(void*a,void*b){return 0;} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={CB:'compare',CB2:'compare2'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('clear','audio_uart_lv_basic_box_clear_454746',0x454746),('free','audio_uart_lv_heap_free',0x44f758),('remove','audio_uart_font_rb_remove',0x5c3600),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args,shape=0,result=0,mutate=0):
  outs=[];s,n=providers[idx];links=shapes[shape]
  for u,cuts,isc in engines:
   u.mem_write(T,bytes([0xa5])*68);u.mem_write(T,W(N if links else 0,CB|1,24));u.mem_write(N,bytes([0xa5])*448);u.mem_write(D,bytes([0xa5])*224)
   pointer=lambda i:0 if i<0 else N+64*i
   for i,(parent,left,right) in enumerate(links):u.mem_write(N+64*i,W(pointer(parent),pointer(left),pointer(right),i&1,D+32*i));u.mem_write(D+32*i,W(i,0x12345678,0x87654321,0))
   calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0x12345678
    if op.startswith('compare'):
     calls.append((op,*r[:2]));ret=result
     if mutate:
      uc.mem_write(T+4,W(CB2|1))
      if mutate==2:
       current=N+((r[1]-D)//32)*64;uc.mem_write(current+4,bytes(8))
    elif op=='clear':
     calls.append((op,*r[:3]));assert r[1]==0;uc.mem_write(r[0],bytes(r[2]))
     if mutate:uc.mem_write(T+12,W(0xdeadbeef))
    elif op=='free':
     calls.append((op,r[0]));uc.mem_write(r[0],bytes([0xdd])*20)
     if mutate:uc.mem_write(T+4,W(0x87654321))
    elif op=='remove':
     calls.append((op,*r[:2]));ret=result
     if mutate:uc.mem_write(T,W(0));uc.mem_write(N,W(0x12345678))
    else:
     fmt,expr=struct.unpack('<II',uc.mem_read(sp,8));item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr))
     if r[2]!=51:item+=(string(uc,struct.unpack('<I',uc.mem_read(sp+8,4))[0]),)
     calls.append(item)
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=5000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000,(s,args,shape,result,mutate)
   outs.append((calls,faults,None if faults or idx in [2,4] else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(T,68)),bytes(u.mem_read(N,448)),bytes(u.mem_read(D,224))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,shape,result,mutate,outs);counts[s]+=1
 for tree,compare,size,mutate in itertools.product([0,T],[0,CB|1],[0,1,24,0xffffffff],[0,1]):check(0,[tree,compare,size],mutate=mutate)
 for tree,shape,result,mutate in itertools.product([0,T],range(len(shapes)),[0,1,127,128,255,256,257,0xffffffff,0x7fffffff,0x80000000],[0,1,2]):check(1,[tree,K],shape,result,mutate)
 for tree,shape,mutate in itertools.product([0,T],range(len(shapes)),[0,1]):check(2,[tree],shape,mutate=mutate)
 for tree,node,result,mutate in itertools.product([0,T],[0,N,N+64],[0,D,D+32],[0,1]):check(3,[tree,node],2,result,mutate)
 for pointer,size,mutate in itertools.product([T,N,D],[0,1,4,12,24,64],[0,1]):check(4,[pointer,size],mutate=mutate)
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_RB_CORE','cases':sum(counts.values()),'by_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual RB memzero wrapper executes; clear/free/remove/logger/comparator controlled child cuts. Six tree shapes,low-byte signed callback edges,current comparator reload,callback mutations,fatal stores compared.','Insertion/removal/rotation/concrete allocator and full-image/layout/byte equality/hardware gates remain open.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
