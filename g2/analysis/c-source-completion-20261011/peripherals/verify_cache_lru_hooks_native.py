from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];DIR=BASE/'root-cache-lru-hooks-round106';SOURCES=[DIR/'lru_alloc_candidate.c',DIR/'lru_hooks_candidate.c',ROOT/'components/audio/uart_thread_source_candidate/display_font_cache_entry.c'];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,V,N,D,K=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000;CB,CB2,DEST=0x600100,0x600104,0x600108;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
providers=[('audio_uart_font_lru_allocate',0x5c2bee),('audio_uart_lv_cache_lru_memzero_5c2af4',0x5c2af4),('audio_uart_font_lru_destroy',0x5c2e0c),('audio_uart_font_lru_add',0x5c2f32)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void*audio_uart_lv_malloc(unsigned n){return 0;} void audio_uart_lv_basic_box_clear_454746(void*a,unsigned b,unsigned c){} void*audio_uart_font_lru_insert(void*a,const void*b){return 0;} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-Ttext=0x100000','-Wl,-e,'+providers[0][0]]+['-Wl,-u,'+s for s,n in providers]+[str(p) for p in SOURCES]+[str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={CB:'size',CB2:'size2',DEST:'destroy'};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('malloc','audio_uart_lv_malloc',0x44f718),('clear','audio_uart_lv_basic_box_clear_454746',0x454746),('insert','audio_uart_font_lru_insert',0x5c2b00),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 counts={s:0 for s,n in providers}
 def check(idx,args=(),allocated=C,node_size=24,current=0,delta=1,insert_result=N,mutate=0):
  outs=[];s,n=providers[idx]
  for u,cuts,isc in engines:
   words=[0xa5a5a5a5]*17;words[0]=V;words[1]=node_size;words[3]=current;words[16]=CB|1;u.mem_write(C,bytes([0xa5])*128);u.mem_write(C,W(*words));u.mem_write(V,W(*([0]*7+[DEST|1]+[0]*2)));u.mem_write(N,W(0,0,0,0,D));u.mem_write(D,bytes([0xa5])*128);calls=[];faults=[]
   def hook(uc,addr,size,user):
    if addr not in cuts:return
    op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0xdeadbeef
    if op=='malloc':calls.append((op,r[0]));assert r[0]==68;ret=allocated
    elif op=='clear':calls.append((op,*r[:3]));assert r[1]==0;uc.mem_write(r[0],bytes(r[2]));ret=0x87654321
    elif op=='destroy':
     calls.append((op,*r[:2]));assert r[0]==C
     if mutate:uc.mem_write(C+12,W(0x87654321))
    elif op=='insert':
     calls.append((op,*r[:2]));ret=insert_result
     if mutate:
      uc.mem_write(C+4,W((node_size+4)&0xffffffff));uc.mem_write(C+64,W(CB2|1))
      if mutate==2:uc.mem_write(C+12,W(0x76543210));uc.mem_write(N+16,W(D+4))
    elif op.startswith('size'):
     calls.append((op,r[0]));ret=delta
     if mutate:uc.mem_write(C+12,W(0xfedcba98))
    else:
     fmt,expr,msg=struct.unpack('<III',uc.mem_read(sp,12));calls.append((op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),string(uc,fmt),string(uc,expr),string(uc,msg)));ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   try:u.emu_start((syms[s] if isc else n)|1,0x600000,count=2000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
   outs.append((calls,faults,None if faults or idx in [1,2] else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,128)),bytes(u.mem_read(V,40)),bytes(u.mem_read(N,20)),bytes(u.mem_read(D,128))));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(s,args,allocated,node_size,current,delta,insert_result,mutate,outs);counts[s]+=1
 for allocated in [0,C,C+4]:check(0,allocated=allocated)
 for pointer,size in itertools.product([C,D],[0,1,4,12,24,64]):check(1,[pointer,size])
 for cache,context,mutate in itertools.product([0,C],[0,1,0x12345678,0xffffffff],[0,1]):check(2,[cache,context],mutate=mutate)
 for node_size,current,delta,insert_result,mutate,context in itertools.product([0,1,24,0xffffffff],[0,0xffffffff],[0,1,0x100,0xffffffff],[0,N],[0,1,2],[0,0xffffffff]):check(3,[C,K,context],node_size=node_size,current=current,delta=delta,insert_result=insert_result,mutate=mutate)
 for cache,key in [(0,0),(0,K),(C,0)]:check(3,[cache,key,0xffffffff])
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_LRU_ALLOC_DESTROY_ADD','cases':sum(counts.values()),'by_provider':counts,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'limits':['Actual native/source LRU zero wrapper and qualified cache-entry-at execute; malloc/clear/insert/destroy/size/logger controlled child cuts.','Destroy caller context preserved; full-word callback delta,mutation,wrapped entry addresses and fatal stores tested. Concrete heap/insertion/backend/data/full-image/hardware gates remain.']};(DIR/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
