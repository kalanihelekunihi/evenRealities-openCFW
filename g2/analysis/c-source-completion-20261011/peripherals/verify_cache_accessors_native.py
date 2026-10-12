from pathlib import Path
import tempfile,subprocess,struct,json,hashlib,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn.arm_const import *
BASE=Path(__file__).parent;ROOT=BASE.parents[2];SRC=BASE/'root-cache-accessors-round99/cache_accessors_candidate.c';BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:];assert hashlib.sha256(BLOB).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
E=0x20001000;W=lambda *v:struct.pack('<'+'I'*len(v),*v)
functions=[('audio_uart_font_cache_has_owner',0x4d5312,False),('audio_uart_font_cache_info',0x4d5396,False),('audio_uart_font_cache_retain',0x4d5278,True),('audio_uart_font_cache_acquire_data',0x4d53c6,False),('audio_uart_font_cache_is_invalid',0x4d536a,False),('audio_uart_font_cache_decrement',0x4d52b2,True),('audio_uart_font_cache_release_data',0x4d5400,True),('audio_uart_font_cache_set_invalid',0x4d533e,True),('audio_uart_font_cache_entry_delete',0x4d54da,True),('audio_uart_font_cache_entry_at',0x4d5452,False),('audio_uart_font_cache_entry_init',0x4d547e,True)]
with tempfile.TemporaryDirectory() as tmp:
 td=Path(tmp);shim=td/'shim.c';shim.write_text('void audio_uart_lv_heap_free(void*a){} void audio_uart_lvgl_log(unsigned a,const char*b,unsigned c,const char*d,...){}');elf=td/'test.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_cache_info',str(SRC),str(shim),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 engines=[]
 for isc in [False,True]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in segs:u.mem_write(a,d)
  cuts={(syms['audio_uart_lv_heap_free'] if isc else 0x44f758)&~1:'free',(syms['audio_uart_lvgl_log'] if isc else 0x44d25c)&~1:'log'};engines.append((u,cuts,isc))
 def string(u,p):return bytes(u.mem_read(p,256)).split(b'\0')[0].decode()
 count=0;counts={}
 for name,native,void in functions:
  cases=[(args,ref,offset,invalid,mutate) for ref,offset,invalid,extra,mutate in itertools.product([0,1,0x7fffffff,0x80000000,0x80000001,0xffffffff],[0,4,16,0xffffffff],[0,128,255],[0,1,255,256,0xffffffff],[False,True]) for args in [[E,extra,offset]]]
  cases+=[([0,0,0],0,0,0,False)]
  if native==0x4d547e:cases+=[([E,0,17],0,0,0,False),([0,E,17],0,0,0,False)]
  if native==0x4d5452:cases+=[([p,x,0],0,0,0,False) for p,x in itertools.product([1,0xffffffff],[1,0xffffffff])]
  local=0
  for args,ref,offset,invalid,mutate in cases:
   outs=[]
   for u,cuts,isc in engines:
    u.mem_write(E,W(0xabcdef01,ref,offset,0x76543200|invalid));calls=[];faults=[]
    def hook(uc,addr,size,user):
     if addr not in cuts:return
     op=cuts[addr];r=[uc.reg_read(v) for v in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];sp=uc.reg_read(UC_ARM_REG_SP)
     if op=='free':calls.append((op,r[0]))
     else:
      fmt=string(uc,struct.unpack('<I',uc.mem_read(sp,4))[0]);item=(op,r[0],string(uc,r[1]),r[2],string(uc,r[3]),fmt)
      if r[2] in [67,121]:item+=(struct.unpack('<I',uc.mem_read(sp+4,4))[0],)
      else:item+=tuple(string(uc,p) for p in struct.unpack('<II',uc.mem_read(sp+4,8)))
      calls.append(item)
     if mutate:uc.mem_write(E+4,W(0x12345678,0xffffffff))
     uc.reg_write(UC_ARM_REG_R0,0xdeadbeef);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def fault(uc,access,addr,size,value,user):faults.append((addr,size,value));return False
    h=u.hook_add(UC_HOOK_CODE,hook);f=u.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],args):u.reg_write(reg,value)
    try:u.emu_start((syms[name] if isc else native)|1,0x600000,count=3000)
    except UcError:assert faults==[(0xffffffff,4,0)],faults
    if not faults:assert u.reg_read(UC_ARM_REG_PC)==0x600000
    outs.append((calls,faults,None if void or faults else u.reg_read(UC_ARM_REG_R0),None if faults else u.reg_read(UC_ARM_REG_SP),bytes(u.mem_read(E,16))));u.hook_del(h);u.hook_del(f)
   assert outs[0]==outs[1],(name,args,ref,offset,invalid,mutate,outs);count+=1;local+=1
  counts[name]=local
 receipt={'status':'PASS_COMPILED_ARM_NATIVE_ALL_SELECTED_CACHE_ACCESSORS','cases':count,'per_provider':counts,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(BLOB).hexdigest(),'native_ranges':['4d5278..4d550c'],'limits':['Actual dependent accessors execute; heap-free/logger child cuts. Bounded refs/offsets/invalid/input values, wrap and callback mutation, exact fatal/warning logs and first UINT32_MAX store.','Not a proof of complete cache backend, allocator behavior, layout/byte equality or hardware.']};(SRC.parent/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
