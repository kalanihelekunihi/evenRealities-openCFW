#!/usr/bin/env python3
"""Native frontend ring/serialization/dequeue with real critical and atomic bodies."""
import hashlib,itertools,json,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();DATA=0x2002d60c;SIZE=4128;RING=DATA+12;HEAD=DATA+4112;MSG=0x20030000;B=0x20002000;CB=0x20002400
FIELDS={'r1_sdk_logger_data':(DATA,SIZE),'r1_sdk_logger_mempool_nrf_balloc_cb':(0x200079d0,8),'r1_sdk_logger_mempool_nrf_balloc_pool_stack':(0x200079c8,8),'r1_sdk_logger_mempool_nrf_balloc_pool_mem':(0x2002d4b4,192)}
SECTIONS={'.data.r1_sdk_logger_mask':0x200079c4,'.nrf_balloc':0xc451c,'.r1.logger.warning.ring':0x798e4,'.r1.logger.warning.nordic':0x79904}
ENTRIES={**{'nrf_log_frontend_std_'+str(i):a for i,a in enumerate((0x799c0,0x799c8,0x799d6,0x799e6,0x799f8,0x79a0c,0x79a28))},'nrf_log_frontend_hexdump':0x79918,'nrf_log_frontend_dequeue':0x796a8,'buf_prealloc':0x566ac,'buffer_is_empty':0x56774,'invalid_packets_omit':0x72848,'dropped_sat16_get':0x5ccfc,'std_n':0x90fec}
def main():
 real_memobj='--real-memobj' in sys.argv
 out=BASE/'sdk-logger-frontend';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'logger.o';receipt=out/('memobj-integration-verification.json' if real_memobj else 'frontend-verification.json');receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 cr=BASE/'sdk-critical/report.json';co=BASE/'sdk-critical/critical-only.o';assert sha(co)==json.loads(cr.read_text())['selected_object_sha256'];pr=BASE/'sdk-power-management/report.json';po=BASE/'sdk-power-management/nrf_atomic-selected.o';assert sha(po)==next(x['object_sha256'] for x in json.loads(pr.read_text())['units'] if x['source'].endswith('/nrf_atomic.c'))
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};comparisons=0;mem_calls=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { '+''.join('.bss.'+n+' '+hex(a)+' (NOLOAD) : { *(.bss.'+n+') } ' for n,(a,z) in FIELDS.items())+''.join(n+' '+hex(a)+' : { *('+n+') } ' for n,a in SECTIONS.items())+'.bss.nrf_nvic_state 0x2002c2fc (NOLOAD) : { *(.bss.nrf_nvic_state) } .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  bindings={n:0x100ee01+i*16 for i,n in enumerate(('nrf_memobj_pool_init','nrf_memobj_alloc','nrf_memobj_get','nrf_memobj_put','nrf_memobj_write','r1_structured_log_mode_get','r1_structured_log_format'))}
  memory_report=BASE/'runtime/report.json';memory_object=memory_report.parent/'memory-runtime.o';assert sha(memory_object)==json.loads(memory_report.read_text())['relocatable_sha256'];extra=[str(memory_object)]
  if real_memobj:
   for name,file,key in [('sdk-memobj','memobj.o','selected_object_sha256')]:
    q=json.loads((BASE/name/'report.json').read_text());path=BASE/name/file;assert sha(path)==q[key];extra.append(str(path))
   bindings={n:a for n,a in bindings.items() if not n.startswith('nrf_memobj_')}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=__start_log_const_data=0','--defsym=__stop_log_const_data=0','--entry=nrf_log_frontend_dequeue',*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),str(co),str(po),*extra,'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3}
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208
  for n,(a,z) in FIELDS.items():assert syms[n]==a and bytes(stock.mem_read(a,z))==bytes(candidate.mem_read(a,z))==bytes(z)
  for n,a in SECTIONS.items():
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',n+'='+str(p),str(elf)],check=True);payload=p.read_bytes();candidate.mem_write(a,payload);assert payload==bytes(stock.mem_read(a,len(payload))),(n,payload,bytes(stock.mem_read(a,len(payload))))
  calls={0x79bfe:'alloc',0x79c90:'get',0x79c9c:'put',0x79cca:'write',0x914ec:'mode',0x91638:'log'};calls.update({bindings[n]&~1:k for n,k in [('nrf_memobj_alloc','alloc'),('nrf_memobj_get','get'),('nrf_memobj_put','put'),('nrf_memobj_write','write'),('r1_structured_log_mode_get','mode'),('r1_structured_log_format','log')] if n in bindings})
  def read32(u,a):return struct.unpack('<I',bytes(u.mem_read(a,4)))[0]
  def ret(u,v=0):u.reg_write(UC_ARM_REG_R0,v);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def textat(u,a):
   data=bytearray()
   for i in range(128):
    v=u.mem_read(a+i,1)[0]
    if not v:return data.decode()
    data.append(v)
   raise AssertionError('unterminated')
  def hook(u,a,size,user):
   nonlocal mem_calls
   f=states[id(u)];args=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
   if a in (0x100ed00,0x100ed10,0x100ed20):
    backend,kind=args[0],(a-0x100ed00)//16;f['trace'].append(('backend',backend,kind,args[1] if kind==0 else None,bytes(u.mem_read(DATA+4116,12))))
    if kind==0 and backend==B and not f['mutated'] and f['mutation']==2:u.mem_write(DATA+4120,struct.pack('<I',1));f['mutated']=True
    ret(u);return
   kind=calls.get(a)
   if not kind:return
   if real_memobj and kind in ('alloc','get','put','write'):
    mem_calls+=1
    if kind=='get' and f['mutation']==1 and not f['mutated']:u.mem_write(DATA+4120,struct.pack('<I',1));f['mutated']=True
    return
   if kind=='alloc':
    assert args[0]==0xc451c;mem_calls+=1;i=f['alloc_index'];f['alloc_index']+=1;ok=f['allocation'][min(i,len(f['allocation'])-1)];p=MSG+i*128 if ok else 0;assert args[1]<=88;f['trace'].append(('alloc',args[1],p));
    if p:f['sizes'][p]=args[1];u.mem_write(p,bytes([0xa7])*128)
    ret(u,p)
   elif kind in ('get','put'):
    mem_calls+=1;f['trace'].append((kind,args[0],bytes(u.mem_read(args[0],f['sizes'][args[0]]))))
    if kind=='get' and f['mutation']==1 and not f['mutated']:u.mem_write(DATA+4120,struct.pack('<I',1));f['mutated']=True
    ret(u)
   elif kind=='write':
    mem_calls+=1;payload=bytes(u.mem_read(args[1],args[2]));f['trace'].append(('write',args[0],payload,args[3]));u.mem_write(args[0]+args[3],payload);ret(u)
   elif kind=='mode':i=f['mode_index'];f['mode_index']+=1;v=f['modes'][min(i,len(f['modes'])-1)];f['trace'].append(('mode',v));ret(u,v)
   elif kind=='log':f['trace'].append(('log',args[0],textat(u,args[1]),textat(u,args[2])));ret(u)
  if real_memobj:
   calls.update({syms[n]&~1:k for n,k in [('nrf_memobj_alloc','alloc'),('nrf_memobj_get','get'),('nrf_memobj_put','put'),('nrf_memobj_write','write')]})
  for u in (stock,candidate):u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def run(u,actions,rd=0,words=(),auto=0,dropped=0,allocation=(1,),modes=(0,),mutation=0,enabled=3,helper_header=None,helper_index=0):
   states[id(u)]=dict(trace=[],alloc_index=0,allocation=allocation,sizes={},modes=modes,mode_index=0,mutation=mutation,mutated=False);f=states[id(u)];u.mem_write(DATA,bytes(SIZE));u.mem_write(DATA,bytes([auto]));u.mem_write(DATA+4,struct.pack('<2I',(rd+len(words))&0xffffffff,rd));u.mem_write(DATA+4124,struct.pack('<I',dropped));u.mem_write(HEAD,struct.pack('<I',B));u.mem_write(0x2002c2fc,bytes(12));u.mem_write(0xe000e000,bytes(4096));u.mem_write(MSG,bytes([0xc9])*0x4000)
   for i,value in enumerate(words):u.mem_write(RING+((rd+i)&1023)*4,struct.pack('<I',value))
   u.mem_write(0x20002500,struct.pack('<3I',0x100ed01,0x100ed11,0x100ed21))
   for i in range(2):u.mem_write(B+i*32,struct.pack('<4I',0x20002500,0,0,CB+i*16));u.mem_write(CB+i*16,struct.pack('<I4B',B+32 if i==0 else 0,i,(enabled>>i)&1,0xa7,0xb8)+b'\xc9'*8)
   u.mem_write(0x20003500,struct.pack('<I',helper_index));u.mem_write(0x20003400,struct.pack('<2I',helper_header or 0,0));u.mem_write(0x20003600,struct.pack('<6I',*[0x12345000+i for i in range(6)]))
   if real_memobj:
    for n,(a,z) in FIELDS.items():
     if n!='r1_sdk_logger_data':u.mem_write(a,bytes(z))
    u.reg_write(UC_ARM_REG_R0,0xc451c);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((0x79c98 if u is stock else syms['nrf_memobj_pool_init'])|1,0x20000100,count=300000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100
    if not allocation[0]:u.mem_write(0x200079d0,struct.pack('<I',0x200079c8))
   u.mem_write(0x20003800,bytes(range(256))*16)
   assert read32(u,0x200079c4)==1023
   results=[]
   for action in actions:
    name=action[0];args=action[1:];u.reg_write(UC_ARM_REG_SP,0x2003f000);u.mem_write(0x2003f000,struct.pack('<4I',*(list(args[4:])+[0]*4)[:4]));u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    
    try:u.emu_start((ENTRIES[name] if u is stock else syms[name])|1,0x20000100,count=300000)
    except Exception as error:raise AssertionError(('native' if u is stock else 'source',action,rd,auto,hex(u.reg_read(UC_ARM_REG_PC)),f['trace'][-8:])) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(action,hex(u.reg_read(UC_ARM_REG_PC)))
    results.append((u.reg_read(UC_ARM_REG_R0) if name in ('nrf_log_frontend_dequeue','buf_prealloc','buffer_is_empty','invalid_packets_omit','dropped_sat16_get') else None,bytes(u.mem_read(DATA,SIZE)),bytes(u.mem_read(CB,32)),bytes(u.mem_read(0x2002c2fc,12)),read32(u,0x20003500),tuple(bytes(u.mem_read(a,z)) for n,(a,z) in FIELDS.items() if n!='r1_sdk_logger_data') if real_memobj else None))
   return results,f['trace']
  def compare(actions,**kw):
   nonlocal comparisons
   a=run(stock,actions,**kw);b=run(candidate,actions,**kw);assert a==b,(actions,kw,a,b);comparisons+=1
  def std(n,mid=0x1c0003,p=0x9a000):return ('nrf_log_frontend_std_'+str(n),mid,p,*[0x12345000+i for i in range(n)])
  for n,rd,mid,p,drop,auto in itertools.product(range(7),(0,1,1021,1022,1023,0xfffffffe),(0,0x1c0003,0xffffffff),(0,0x9a000,0x20003000,0xffffffff),(0,1,65535,65536,0xffffffff),(0,1)):compare([std(n,mid,p)],rd=rd,dropped=drop,auto=auto)
  for n,free,rd,old_drop in itertools.product(range(7),(0,1,2,3,4,5),(0,1019),(0,0x12340000,0xffff0000)):
   occupied=1024-free;occupied-=occupied%2;words=[1,old_drop]* (occupied//2);compare([std(n)],rd=rd,words=words,dropped=65534)
  for n,rd,allocation,mode,mutation in itertools.product((0,1,4,6,15),(0,1022,1023),((1,),(0,1)),((0,),(1,),(2,),(0,4,2)),range(3)):
   header=1|(3<<3)|(n<<6)|(0x9a000<<10);words=[header,0x1234001c,*range(n)];compare([('nrf_log_frontend_dequeue',)],rd=rd,words=words,allocation=allocation,modes=mode,mutation=mutation)
  for length,rd in itertools.product((0,1,3,4,5,16,79,80,81,127),(0,1018,1021,1023)):
   words=[2|(3<<3)|(length<<22),0x1234001c,*[0x12345678]*( (length+3)//4 )];compare([('nrf_log_frontend_dequeue',)],rd=rd,words=words)
  for rd,n in itertools.product((0,1021,1023),(0,1,4)):
   invalid=1|4|(n<<6);words=[invalid,0,*range(n),1|(3<<3),0];compare([('nrf_log_frontend_dequeue',)],rd=rd,words=words)
  for kind,n,rd in itertools.product((1,2),(0,1,4),(0,1021,1023)):
   invalid=kind|4|((n<<6) if kind==1 else (n<<22));compare([('nrf_log_frontend_dequeue',)],rd=rd,words=[invalid,0,*range(n),1|(3<<3),0])
  for length,rd in itertools.product((0,8,16,80),(0,1023)):
   packet=[2|(length<<22),0x12340000,*[0x12345678]*(length//4)];compare([std(4)],rd=rd,words=packet+[1,0]*((1024-len(packet))//2))
  for std_flag,n,rd in itertools.product((0,1),(0,1,4,20),(0,1023)):
   compare([('buf_prealloc',n,0x20003500,std_flag)],rd=rd)
  for kind,progress,n,index in itertools.product(range(4),(0,1),(0,1,4,15),(0,1,0xfffffffe)):
   header=kind|(progress<<2)|((n<<22) if kind==2 else (n<<6));compare([('invalid_packets_omit',0x20003400,0x20003500)],helper_header=header,helper_index=index)
  for dropped in (0,1,65535,65536,0x7fffffff,0x80000000,0xffffffff):compare([('dropped_sat16_get',)],dropped=dropped)
  for n,rd in itertools.product(range(7),(0,1021,1023)):compare([('std_n',0x1c0003,0x9a000,0x20003600,n)],rd=rd)
  for words in ((),(1,0)):compare([('buffer_is_empty',)],words=words)
  for mode in ((0,),(1,),(2,),(4,),(7,)):compare([('nrf_log_frontend_dequeue',)]*3,words=[1|(3<<3),0],allocation=(0,1),modes=mode)
  for length,rd,mid,drop,auto in itertools.product((0,1,2,3,4,5,7,8,9,16,79,80,81,127,255,511,1021,1023),(0,1,1019,1021,1022,1023,0xfffffffe),(0,0x1c0003,0xffffffff),(0,1,65535,0xffffffff),(0,1)):
   compare([('nrf_log_frontend_hexdump',mid,0x20003800,length)],rd=rd,dropped=drop,auto=auto)
  for length,rd in itertools.product((1,5,80,255,1023),(0,1021,1023)):
   compare([('nrf_log_frontend_hexdump',0x1c0003,0x20003800,length)],rd=rd,words=[1,0]*512)
  for length,rd in itertools.product((1024,2047,4088),(0,1021,1023)):
   compare([('nrf_log_frontend_hexdump',0x1c0003,0x20003800,length)],rd=rd)
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),comparisons=comparisons,memobj_calls_per_implementation=mem_calls//2,critical_report_sha256=sha(cr),atomic_store_report_sha256=sha(pr),source_owned_zero_bytes=sum(z for a,z in FIELDS.values()),mask_initial_bytes_compared=4,mempool_descriptor_bytes_compared=20,warning_string_bytes_compared=40,actual_memobj=real_memobj,memobj_report_sha256=sha(BASE/'sdk-memobj/report.json') if real_memobj else None,memory_report_sha256=sha(memory_report),scope='Actual frontend standard0..6/hexdump, dequeue, overflow/skip and atomic/critical code; ring wrap, saturation, in-progress entries, memobj failure, hexdump clamp/wrap, backend delivery and skip mutations',limitations=['Backend callbacks remain fixtures; memory-object/pool bodies execute when actual_memobj is true. Failed-allocation scenarios use a depleted pool in that mode.','Canonical bool state, valid bounded packet streams and finite callback scripts; lengths1024..4088 are producer-only packing checks because the ten-bit header length wraps; malformed nonterminating streams and real concurrency remain gates.','Production logger initialization/registration, physical transport, original compiler/link identity and byte equality remain unresolved; memobj bodies are exercised only in actual_memobj mode.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'frontend comparisons;',mem_calls//2,'memobj API calls')
if __name__=='__main__':main()
