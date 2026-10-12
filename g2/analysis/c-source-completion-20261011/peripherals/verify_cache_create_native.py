from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];FOLDER=BASE/'root-cache-acquire-create-round100';WRAPPER=BASE/'root-cache-add-round97/cache_add_candidate.c';INTERNAL=FOLDER/'cache_create_candidate.c';ENTRY_SRC=BASE/'root-cache-accessors-round99/cache_accessors_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,K,E,V,V2,DATA=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000,0x20002fc0;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_lock_core(void*a){return 0;} unsigned audio_uart_lv_unlock_core(void*a){return 0;} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}')
 elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffunction-sections','-fdata-sections','-nostdlib','-Wl,--gc-sections','-Wl,-u,audio_uart_font_cache_add','-Wl,-u,audio_uart_lv_cache_evict_one_4d5172','-Wl,-e,audio_uart_lv_cache_add_4d4eea','-Wl,-Ttext=0x100000',str(WRAPPER),str(INTERNAL),str(ENTRY_SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 # Stable synthetic callback identities are outside native bodies.
 addresses={op:0x600100+i*4 for i,op in enumerate(['space','victim','remove','create','destroy','space2','victim2','remove2','create2','destroy2','lookup','lookup2','initialize','initialize2'])}
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={a:op for op,a in addresses.items()}
  cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('lock','audio_uart_lv_lock_core',0x4d4666),('unlock','audio_uart_lv_unlock_core',0x4d4696),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]})
  engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 def table(secondary=False):
  suffix='2' if secondary else '';v=[0]*10
  for index,name in [(3,'lookup'),(4,'create'),(5,'remove'),(8,'victim'),(9,'space')]:v[index]=addresses[name+suffix]|1
  return W(*v)
 sequences=[[0],[1],[0x100],[0x101],[3],[2,0],[0x102,0x100],[2,1],[2,2,0],[2,2,0x101]]
 count=0
 for api,native,return_void in [('audio_uart_font_cache_add',0x4d4f90,False)]:
  for seq,victim,created,max_size,ref,mutate,found,initialized,size_nonzero in itertools.product(sequences,[False,True],[False,True],[0,0x12345678],[0,0xffffffff],[0,1,2],[False,True],[0,1,0x100,0x101,0xffffffff],[False,True]):
   outs=[]
   for u,cuts,isc in engines:
    u.mem_write(C,W(V,0,max_size,1 if size_nonzero else 0,0,addresses['initialize']|1,addresses['destroy']|1,0,0));u.mem_write(V,table());u.mem_write(V2,table(True));u.mem_write(K,W(0xdeadbeef));u.mem_write(E,W(C,ref,64,0));u.mem_write(DATA,bytes([0xaa])*64);calls=[];faults=[];state={'room':0,'victims':0}
    def hook(uc,addr,size,user):
     if addr not in cuts:return
     op=cuts[addr];base=op.removesuffix('2');r=[uc.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
     if base=='lookup':
      calls.append((op,*r[:3]));assert r[:3]==[C,K,0xffffffff];ret=E if found else 0
      if mutate:uc.mem_write(C,W(V2));uc.mem_write(C+20,W(addresses['initialize2']|1))
     elif base=='initialize':
      calls.append((op,*r[:2]));assert r[:2]==[DATA,0xffffffff];ret=initialized
      if mutate:uc.mem_write(C,W(V));uc.mem_write(C+24,W(addresses['destroy2']|1))
     elif base=='space':
      calls.append((op,*r));assert r==[C,K,0,0xffffffff];ret=seq[min(state['room'],len(seq)-1)];state['room']+=1
      if state['room']>8:raise AssertionError('unexpected unbounded reserve')
      if mutate:uc.mem_write(C,W(V2));uc.mem_write(C+8,W(0x87654321))
     elif base=='victim':
      calls.append((op,*r[:2]));assert r[:2]==[C,0xffffffff];ret=E if victim else 0;state['victims']+=1
      if mutate==2:uc.mem_write(C,W(V));uc.mem_write(C+24,W(addresses['destroy2']|1))
     elif base=='remove':
      calls.append((op,*r[:3]));assert r[:3]==[C,E,0xffffffff]
      if mutate:uc.mem_write(C+24,W(addresses['destroy2']|1))
     elif base=='create':
      calls.append((op,*r[:3]));assert r[:3]==[C,K,0xffffffff];ret=E if created else 0
     elif base=='destroy':calls.append((op,*r[:2]));assert r[:2]==[DATA,0xffffffff]
     elif base=='free':calls.append((op,r[0]));assert r[0]==DATA
     elif base in ['lock','unlock']:
      calls.append((op,r[0]));assert r[0]==C+28;ret=0xdeadbeef
      if base=='lock' and mutate==2:uc.mem_write(C+8,W(7))
      if base=='unlock' and mutate:uc.mem_write(C+12,W(0xabcdef01))
     else:
      fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
      if r[2] in [149,150]:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
      elif r[2]==345:item+=struct.unpack('<II',uc.mem_read(sp+4,8))
      elif r[2]!=331:raise AssertionError(r[2])
      calls.append(item)
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
    h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    args=[C,0xffffffff] if native==0x4d5172 else [C,K,0xffffffff]
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,value)
    try:u.emu_start((syms[api] if isc else native)|1,0x600000,count=10000)
    except UcError:assert faults==[(0xffffffff,4,0)]
    assert not faults and u.reg_read(UC_ARM_REG_PC)==0x600000
    outs.append((calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,36)),bytes(u.mem_read(E,16)),bytes(u.mem_read(DATA,64))));u.hook_del(h);u.hook_del(f)
   assert outs[0]==outs[1],(api,seq,victim,created,max_size,ref,mutate,found,initialized,size_nonzero,outs);count+=1
 # Wrapper cache/key null assertions: dependencies must not run.
 for cache,key in [(0,K),(C,0),(0,0)]:
  outs=[]
  for u,cuts,isc in engines:
   calls=[];faults=[];log=next(a for a,op in cuts.items() if op=='log')
   def hook(uc,addr,size,user):
    if addr!=log:return
    r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];v=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12));calls.append((r[0],string(uc,r[1]),r[2],string(uc,r[3]),*[string(uc,p) for p in v]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
   h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,cache);u.reg_write(UC_ARM_REG_R1,key)
   try:u.emu_start((syms['audio_uart_font_cache_add'] if isc else 0x4d4f90)|1,0x600000,count=1000)
   except UcError:assert faults==[(0xffffffff,4,0)]
   outs.append((calls,faults));u.hook_del(h);u.hook_del(f)
  assert outs[0]==outs[1],(cache,key,outs);count+=1
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_ACQUIRE_OR_CREATE','cases':count,'source_sha256':hashlib.sha256(INTERNAL.read_bytes()).hexdigest(),'wrapper_fixture_sha256':hashlib.sha256(WRAPPER.read_bytes()).hexdigest(),'entry_sha256':hashlib.sha256(ENTRY_SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['4d4f90..4d5094'],'limits':['Actual internal/evict/acquire/retain/getter/delete bodies execute. Mutex/vtable callbacks/heap-free/logger are child cuts; class/ops mutation and upper-byte reserve returns exercised.','Full native acquire-or-create paths, low-byte initializer results, class/ops changes and existing-entry fast acquire verified; concrete callbacks/tree/allocator behavior and full-image gates remain.']};(FOLDER/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
