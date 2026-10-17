#!/usr/bin/env python3
"""Direct and table-dispatch callback contracts with explicit service/log/free fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-event-callbacks';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-event-callbacks-runtime.o';assert sha(obj)==b['linked_sha256'];contracts=json.loads((OUT/'callback-contracts.json').read_text());providers=json.loads((OUT/'provider-map.json').read_text());tables=json.loads((BASE/'native-event-table-prefixes/prefix-contracts.json').read_text())['tables'];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};counts=dict(direct=0,composed=0,faults=0);by_body={r['address']:0 for r in contracts['callbacks']};digest=hashlib.sha256();observations={a:0 for a in providers};observations['free']=0
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 with tempfile.TemporaryDirectory(prefix='r1-callback-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';text=d/'text.bin';rom=''.join(' .s'+x['address'][2:]+' '+x['address']+' : { *('+x['section']+') } ' for x in json.loads((OUT/'text-spans.json').read_text()) if 'section' in x);ram=''.join(' .'+t['family']+' '+t['address']+' : { *('+t['section']+') } ' for t in tables);ld.write_text('SECTIONS { '+rom+ram+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:0x1100001+256*i for i,n in enumerate(providers.values())};bindings['vPortFree']=0x110f001;subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','r1_native_event_dispatch','-T',str(ld),*[f'--defsym={n}={v}' for n,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);symbols={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};hooks={int(a,16):a for a in providers};hooks.update({bindings[n]&~1:a for a,n in providers.items()});hooks[0x95d48]=hooks[0x110f000]='free';sdk={0x799c8:1,0x799d6:2,0x799e6:3,0x799f8:4,0x79a0c:5};source_tables={t['family']:b'' for t in tables}
  for t in tables:
   p=d/(t['family']+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+t['family'],'-O','binary',str(elf),str(p)],check=True);source_tables[t['family']]=p.read_bytes()
  def hook(u,a,size,_):
   if a not in hooks:return
   key=hooks[a];st=states[id(u)];c=st['case'];args=[u.reg_read(x) for x in REGS];value=c['result'];extra=[]
   if key=='free':args=args[:1]
   elif key=='0x914ec':value=c['modes'][min(st['mode_index'],len(c['modes'])-1)];st['mode_index']+=1;args=[value]
   elif key=='0x91638':
    count=(args[0]>>22)&15;extra=list(struct.unpack('<'+'I'*max(0,count-1),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-1)*4)));args=args[:3+min(count,1)]
   elif int(key,16) in sdk:
    count=sdk[int(key,16)];extra=list(struct.unpack('<'+'I'*max(0,count-2),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-2)*4)));args=args[:2+min(count,2)]
   elif key=='0x735e0':u.mem_write(args[0],bytes.fromhex(c['data'])[:10]);extra=[bytes(u.mem_read(args[0],10)).hex()]
   elif key=='0x6c66c' and D<=args[1]<D+500:u.mem_write(args[0],bytes(u.mem_read(args[1],10)));extra=[bytes(u.mem_read(args[0],10)).hex()]
   if c['mutation'] and key not in ['free','0x914ec'] and not key.startswith('0x799') and key!='0x91638':u.mem_write(D,bytes.fromhex('efbeadde'))
   st['trace'].append([key,args,extra,value]);
   if not st['side']:observations[key]+=1
   for reg,v in zip(REGS,[value,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,0x10000);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  cases=[]
  for row,payload,length,result,modes,mutation,data in itertools.product(contracts['callbacks'],[0,1,D,D+1,0x2003ffff],[0,1,4,8,9,12,16,0xffffffff],[0,1,0xffffffff],[[0],[7],[0,4,2]],range(2),['0001020380ff007fff7f','ffffffffffffffffffff']):cases.append(dict(row=row,payload=payload,length=length,result=result,modes=modes,mutation=mutation,data=data,composed=False))
  for c in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes.fromhex(c['data'])*51);u.mem_write(SP-1024,b'\x96'*2048)
    for t in tables:u.mem_write(int(t['address'],16),source_tables[t['family']] if side else struct.pack('<'+'I'*len(t['words']),*t['words']))
    args=[c['payload'],c['length'],0x12345678,0x98765432];entry=symbols[c['row']['symbol']] if side else int(c['row']['address'],16)
    if c['composed']:u.mem_write(D+0x400,struct.pack('<4I',0x12345678,c['event_id']|0xabcd0000,c['length']|0xbeef0000,c['payload']));args[0]=D+0x400;entry=symbols['r1_native_event_dispatch'] if side else 0x8d888
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]=dict(case=c,side=side,trace=[],mode_index=0,fault=None)
    try:u.emu_start(entry|1,0x20000100,count=10000)
    except UcError:
     assert states[id(u)]['fault'],(c,side,hex(u.reg_read(UC_ARM_REG_PC)))
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(c,side)
    results.append([None if st['fault'] or c['composed'] else [u.reg_read(x) for x in REGS],st['trace'],st['fault'],bytes(u.mem_read(D,512)).hex()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(case=c,results=results),indent=2)+'\n');raise AssertionError(c)
   counts['composed' if c['composed'] else 'direct']+=1;counts['faults']+=bool(results[0][2]);by_body[c['row']['address']]+=1;digest.update(json.dumps([c,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=counts['direct']+counts['composed'],counts=counts,by_body=by_body,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),all_37_callback_bodies_execute=True,source_dispatch_tables_and_callbacks_composed=False,composed_dispatch_raw_abi_probe_sha256=sha(OUT/'dispatch-raw-abi-probe.json'),services_logging_and_free_are_fixtures=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,full_table_extents_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
