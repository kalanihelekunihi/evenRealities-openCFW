from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];FOLDER=BASE/'root-cache-find-drop-round101';FIND=FOLDER/'cache_find_candidate.c';DROP=FOLDER/'cache_drop_candidate.c';ENTRY=ROOT/'components/audio/uart_thread_source_candidate/display_font_cache_entry.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
C,K,E,V,V2=0x20001000,0x20002000,0x20003000,0x20004000,0x20005000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
callbacks={op:0x600100+4*i for i,op in enumerate(['lookup','lookup2','remove','remove2','destroy','destroy2'])}
functions=[('audio_uart_font_cache_find',0x4d4dca,False),('audio_uart_font_cache_remove',0x4d4e72,True),('audio_uart_font_cache_drop',0x4d5094,True),('audio_uart_lv_cache_drop_internal_4d511c',0x4d511c,True)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('unsigned audio_uart_lv_lock_core(void*a){return 0;} unsigned audio_uart_lv_unlock_core(void*a){return 0;} void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cache_find',str(FIND),str(DROP),str(ENTRY),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={addr:op for op,addr in callbacks.items()};cuts.update({(syms[s] if isc else n)&~1:op for op,s,n in [('lock','audio_uart_lv_lock_core',0x4d4666),('unlock','audio_uart_lv_unlock_core',0x4d4696),('free','audio_uart_lv_heap_free',0x44f758),('log','audio_uart_lvgl_log',0x44d25c)]});engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 def table(suffix=''):
  t=[0]*10;t[3]=callbacks['lookup'+suffix]|1;t[5]=callbacks['remove'+suffix]|1;return W(*t)
 count=0;per={}
 for name,native,void in functions:
  cases=[(C,E if native==0x4d4e72 else K,size,found,ref,invalid,mutate) for size,found,ref,invalid,mutate in itertools.product([0,1],[False,True],[0,1,2,0x80000000,0xffffffff],[0,1,128,255],[0,1,2])]
  if native in [0x4d4dca,0x4d5094]:cases+=[(0,K,0,False,0,0,0),(C,0,0,False,0,0,0),(0,0,0,False,0,0,0)]
  elif native==0x4d4e72:cases+=[(C,0,0,False,0,0,0),(0,0,0,False,0,0,0)]
  local=0
  for cache,key,size,found,ref,invalid,mutate in cases:
   outs=[]
   for u,cuts,isc in engines:
    u.mem_write(C,W(V,0,4096,size,0,0,callbacks['destroy']|1,0,0));u.mem_write(V,table());u.mem_write(V2,table('2'));u.mem_write(E,W(C,ref,64,0xaabbcc00|invalid));u.mem_write(K,W(0x12345678));calls=[];faults=[]
    def hook(uc,addr,length,user):
     if addr not in cuts:return
     op=cuts[addr];base=op.removesuffix('2');r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP);ret=0
     if base=='lookup':
      calls.append((op,*r[:3]));assert r[:3]==[C,K,0xffffffff];ret=E if found else 0
      if mutate:uc.mem_write(C,W(V2));uc.mem_write(C+24,W(callbacks['destroy2']|1))
     elif base=='remove':
      calls.append((op,*r[:3]));assert r[:3]==[C,E,0xffffffff]
      if mutate:uc.mem_write(E+8,W(16));uc.mem_write(C+24,W(callbacks['destroy2']|1))
     elif base=='destroy':
      calls.append((op,*r[:2]));off=struct.unpack('<I',uc.mem_read(E+8,4))[0];assert r[:2]==[(E-off)&0xffffffff,0xffffffff]
      if mutate:uc.mem_write(E+4,W(2,4))
     elif base=='free':calls.append((op,r[0]))
     elif base in ['lock','unlock']:
      calls.append((op,r[0]));assert r[0]==C+28;ret=0xffffffff
      if base=='lock' and mutate==2:uc.mem_write(C,W(V2));uc.mem_write(C+12,W(1));uc.mem_write(C+24,W(callbacks['destroy2']|1))
      if base=='unlock' and mutate:uc.mem_write(C+12,W(0xdeadbeef))
     else:
      fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
      if r[2] in [67,121]:item+=(struct.unpack('<I',uc.mem_read(sp+4,4))[0],)
      else:item+=tuple(string(uc,v) for v in struct.unpack('<II',uc.mem_read(sp+4,8)))
      calls.append(item)
      if mutate and r[2] in [67,121]:uc.mem_write(E+4,W(1))
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def fault(uc,access,addr,length,value,user):faults.append((addr,length,value));return False
    h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[cache,key,0xffffffff]):u.reg_write(reg,value)
    try:u.emu_start((syms[name] if isc else native)|1,0x600000,count=5000)
    except UcError:assert faults==[(0xffffffff,4,0)],faults
    if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
    outs.append((calls,faults,None if void or faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(C,36)),bytes(u.mem_read(E,16))));u.hook_del(h);u.hook_del(f)
   assert outs[0]==outs[1],(name,cache,key,size,found,ref,invalid,mutate,outs);count+=1;local+=1
  per[name]=local
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_CACHE_FIND_RELEASE_DROP','cases':count,'per_provider':per,'find_sha256':hashlib.sha256(FIND.read_bytes()).hexdigest(),'drop_sha256':hashlib.sha256(DROP.read_bytes()).hexdigest(),'entry_sha256':hashlib.sha256(ENTRY.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['4d4dca..4d4eea','4d5094..4d5172'],'limits':['Actual accessors and drop internal execute; mutex/class/cleanup/heap-free/logger child cuts. Mutation, signed refs and invalid states exercised.','Exact logger and first assertion store verified. Concrete cache backend, layout/byte equality and hardware remain open.']};(FOLDER/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
