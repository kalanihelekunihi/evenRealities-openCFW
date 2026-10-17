#!/usr/bin/env python3
"""Compare source log reads and actual count->iterator->reader->decoder chain."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-flashdb-sector-read';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;DB=0x20010000;ARG=DB+256;LOCK=0x20001000;UNLOCK=0x20001010;CALLBACK=0x20001020
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';obj=OUT/'native_flashdb_sector_read.o';logobj=BASE/'native-flashdb-log-read/native_flashdb_log_read.o';iteratorobj=BASE/'native-flashdb-iterator/native_flashdb_iterator.o';countobj=BASE/'native-flashdb-query-count/native_flashdb_query_count.o';digest=hashlib.sha256();counts={'direct':0,'count_composed':0};observed={'callbacks':0,'reads':0,'locks':0,'unlocks':0,'logs':0};states={}
 spans=[(x['symbol'],int(x['address'],16),x['source_span_bytes']) for x in c['bodies']]+[('r1_fdb_sector_function_name',0x9bdb9,17)]+[(x['symbol'],int(x['address'],16),x['source_span_bytes']) for x in json.loads((BASE/'native-flashdb-log-read/contracts.json').read_text())['bodies']]+[(x['symbol'],int(x['address'],16),x['source_span_bytes']) for x in json.loads((BASE/'native-flashdb-iterator/contracts.json').read_text())['bodies']]+[('r1_health_sync_provider_00063cb4',0x63cb4,139),('r1_fdb_native_query_count_cb',0x87428,18),('r1_fdb_native_db_path',0x3f014,14)]
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS {\n'+''.join('.s%d 0x%x : { *(%s) }\n'%(i,a,'.r1.fdb.sector_function_name' if n=='r1_fdb_sector_function_name' else '.text.'+('r1_fdb_native_query_count' if n=='r1_health_sync_provider_00063cb4' else n)) for i,(n,a,l) in enumerate(spans))+'/DISCARD/ : { *(.ARM.exidx*) } }\nr1_native_printf = 0x38061; r1_native_memory_move = 0x2775d; r1_fdb_native_partition_read = 0x631e9;\n');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(logobj),str(iteratorobj),str(countobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE)
  replacements=[];proof=[]
  for i,(name,a,length) in enumerate(spans):
   p=td/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.s'+str(i),'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();assert len(data)==length,(name,len(data),length);native=image[a-0x27000:a-0x27000+length];assert data==native,(name,[(j,x,y) for j,(x,y) in enumerate(zip(data,native)) if x!=y][:10]);replacements.append((a,data));proof.append(dict(symbol=name,address=hex(a),size=length,sha256=sha(p)))
  def put(u,p,v):u.mem_write(p,struct.pack('<I',v&0xffffffff))
  def get(u,p):return struct.unpack('<I',u.mem_read(p,4))[0]
  def sector(addr,status=3):
   d=bytearray(40);d[0]=1;d[1]=status;struct.pack_into('<5I',d,4,addr,0x304c5354,addr//256*100+10,addr//256*100+30,addr+144);return bytes(d)
  def hook(u,a,size,_):
   s=states[id(u)];case=s['case'];r=[u.reg_read(x) for x in REGS];ret=True
   if a==0x631e8:
    assert r[0]==DB+320;index=r[1]
    if r[3]==80:
     base=index;secstatus=case['sector_status'] if base==256 else 3;data=bytearray(b'\xff'*80)
     if secstatus in [1,2,3]:data[(secstatus-1)*4]=0
     struct.pack_into('<5I',data,12,0x304c5354,base//256*100+10,base//256*100+30,base+144,0xffffffff);data[32]=0
     s['trace'].append(['partition-header',r])
     if case['read_mode']!=2:u.mem_write(r[2],bytes(data))
     u.reg_write(UC_ARM_REG_R0,0xffffffff if case['read_mode'] else 80)
    else:
     assert r[3]==32;base=index//256*256;slot=(index-base-80)//32;time=base//256*100+10+slot*10;status=0 if slot not in [0,1,2] or case['unused'] and slot%2==0 else 2
     s['trace'].append(['partition-log',r,index,time,status]);data=bytearray(b'\xff'*32)
     if status:data[(status-1)*4]=0
     struct.pack_into('<III',data,20,time&0xffffffff,4,index+128);u.mem_write(r[2],bytes(data));u.reg_write(UC_ARM_REG_R0,32)
    observed['reads']+=1
   elif a==0x2775c:
    assert r[2]==40;u.mem_write(r[0],bytes(u.mem_read(r[1],r[2])));s['trace'].append(['copy',r])
   elif a==0x38060:
    text=bytes(u.mem_read(r[0],80)).split(b'\0')[0].decode();s['trace'].append(['log',r,text]);u.reg_write(UC_ARM_REG_R0,7);u.reg_write(UC_ARM_REG_R1,0xa1);u.reg_write(UC_ARM_REG_R2,0xa2);u.reg_write(UC_ARM_REG_R3,0xa3);observed['logs']+=1
   elif a in [LOCK,UNLOCK,UNLOCK+0x20]:
    assert r[0]==DB;s['trace'].append(['lock' if a==LOCK else 'unlock',r,a]);observed['locks' if a==LOCK else 'unlocks']+=1
    if a==LOCK and case['mutation']:put(u,DB+32,UNLOCK+0x21)
   elif a==CALLBACK:
    assert r[0]==SP-116 and r[1]==ARG;s['trace'].append(['callback',r,bytes(u.mem_read(r[0],20)).hex()]);s['callbacks']+=1;put(u,ARG,get(u,ARG)+1);u.reg_write(UC_ARM_REG_R0,int(case['stop'] and s['callbacks']>=case['stop']));observed['callbacks']+=1
   else:ret=False
   if ret:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,data in replacements:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(init=1,from_time=0,to_time=250,callback=1,locks=1,sector_status=3,read_mode=0,unused=0,stop=0,mutation=0,status=2)
  cases=[]
  for composed,init,times,locks,mutation in itertools.product([False,True],[0,1,255],[(0,250),(250,0),(10,10),(11,29),(29,11),(100,200),(200,100),(0x7fffffff,0x80000000),(0x80000000,0x7fffffff)],range(2),range(2)):
   cases.append(dict(default,composed=composed,init=init,from_time=times[0],to_time=times[1],locks=locks,mutation=mutation))
  for composed,sector_status,read_mode,unused,stop,times in itertools.product([False,True],[0,1,2,3,255],range(3),range(2),[0,1,2],[(0,250),(250,0),(11,29),(29,11)]):cases.append(dict(default,composed=composed,sector_status=sector_status,read_mode=read_mode,unused=unused,stop=stop,from_time=times[0],to_time=times[1]))
  for init,callback,times in itertools.product([0,1,255],range(2),[(0,250),(250,0)]):cases.append(dict(default,composed=False,init=init,callback=callback,from_time=times[0],to_time=times[1]))
  for case in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(DB,b'\x96'*512);put(u,DB,DB+300);put(u,DB+8,DB+320);put(u,DB+12,256);put(u,DB+16,768);put(u,DB+20,0);u.mem_write(DB+24,bytes([case['init'],0,0,0]));put(u,DB+28,LOCK+1 if case['locks'] else 0);put(u,DB+32,UNLOCK+1 if case['locks'] else 0);u.mem_write(DB+40,sector(512,2));u.mem_write(DB+300,b'logs\0');u.mem_write(DB+324,b'path\0');put(u,ARG,0);u.mem_write(SP-512,b'\x96'*1024);put(u,SP,ARG)
    args=[DB,case['from_time'],case['to_time'],case['status'] if case['composed'] else CALLBACK+1 if case['callback'] else 0]
    for r,v in zip(REGS,args):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=case,trace=[],callbacks=0);states[id(u)]=s
    u.emu_start(0x63cb5 if case['composed'] else 0x63ad9,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100,(case,side,hex(u.reg_read(UC_ARM_REG_PC)))
    assert u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)]
    if case['read_mode']==0 and case['sector_status']==3 and not case['unused'] and not case['stop']:
     lo=min(struct.unpack('<i',struct.pack('<I',case['from_time']))[0],struct.unpack('<i',struct.pack('<I',case['to_time']))[0]);hi=max(struct.unpack('<i',struct.pack('<I',case['from_time']))[0],struct.unpack('<i',struct.pack('<I',case['to_time']))[0]);expected=sum(lo<=t<=hi for t in [10,20,30,110,120,130,210,220,230])
     if case['composed']:assert u.reg_read(UC_ARM_REG_R0)==(expected if case['init'] else 0),(case,u.reg_read(UC_ARM_REG_R0),expected)
     else:assert s['callbacks']==(expected if case['callback'] else 0),(case,s['callbacks'],expected)
    results.append([[u.reg_read(r) for r in REGS],s['trace'],bytes(u.mem_read(DB,512)).hex(),bytes(u.mem_read(SP-512,1024)).hex()])
   assert results[0]==results[1],case;counts['count_composed' if case['composed'] else 'direct']+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations=observed,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_bytes=sum(x['size'] for x in proof),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),log_object_sha256=sha(logobj),count_object_sha256=sha(countobj),iterator_object_sha256=sha(iteratorobj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_count_iterator_sector_log_flash_adapter_status_decoder_and_callback_execute=True,partition_io_memory_copy_lock_custom_callback_and_printf_are_fixtures=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
