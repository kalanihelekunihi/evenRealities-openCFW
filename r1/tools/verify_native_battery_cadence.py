#!/usr/bin/env python3
"""Replay charging cadence state, tick wrap, mutable thresholds and provider ordering."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-cadence';D=0x20016b84;B=0x20006890;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P={'osKernelGetTickCount':0x7d28c,'osKernelGetTickFreq':0x7d2a4,'r1_batcfg_byte0_get':0x7bb44}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_cadence.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 p=OUT/'rea-4fe70.json';p.write_bytes((BASE/'native-battery-runtime/rea-next-4fe70-body.json').read_bytes());q=json.loads(p.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==194;evidence[p.name]=sha(p)
 socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x4fe70&length=204']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x4fe70-0x27000:0x4fe70-0x27000+204];p=OUT/'ghidra-body.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 rng=random.Random(0x4fe70);cases=[]
 for initial,timestamp,frequency,kind,tablemode in itertools.product((0,84,85,89,90,94,95,99,100,255),(0,1,0xffffffff),(0,1,1000,0xffffffff),(0,1,2,3,4,5,0xffffffff),(0,1,2)):
  cases.append(dict(initial=initial,timestamp=timestamp,frequency=frequency,kind=kind,thresholds=[0]*16 if tablemode==0 else list(range(1,17)) if tablemode==1 else [65535]*16,key=timestamp if kind&1 else 0,ticks=(0xfffffff0,0x100),last=0xfffffff0,accumulator=0xfffffff0 if kind&1 else 179,level=(initial+1)&255,voltage=4341 if kind&1 else 4340,flag=5,mutation=False))
 for _ in range(4096):cases.append(dict(initial=rng.randrange(256),timestamp=rng.choice((0,1,0xffffffff,rng.getrandbits(32))),frequency=rng.choice((0,1,2,1000,0xffffffff)),kind=rng.choice((0,1,2,3,4,5,0xffffffff)),thresholds=[rng.choice((0,1,2,30,180,65535)) for _ in range(16)],key=rng.choice((0,1,0xffffffff)),ticks=(rng.getrandbits(32),rng.getrandbits(32)),last=rng.getrandbits(32),accumulator=rng.getrandbits(32),level=rng.randrange(256),voltage=rng.choice((0,4340,4341,65535,0xffffffff)),flag=rng.choice((0,4,5,255)),mutation=bool(rng.getrandbits(1))))
 machines=[];states={};counts={n:0 for n in P};divisions=0
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_battery_runtime_context='+hex(B),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  def hook(u,a,size,_):
   nonlocal divisions
   if a==0x274e8:divisions+=1
   if a not in kinds:
    if u is machines[1] and a<0x1000000 and a!=0x20000100:raise AssertionError(('source native provider',hex(a)))
    return
   f=states[id(u)];n=kinds[a];f['trace'].append((n,bytes(u.mem_read(D,68)),bytes(u.mem_read(B,96))))
   if n=='osKernelGetTickCount':value=f['ticks'][f['tick_index']];f['tick_index']+=1
   elif n=='osKernelGetTickFreq':
    value=f['frequency']
    if f['mutation']:u.mem_write(D+64,struct.pack('<I',0xfffffff0));u.mem_write(D+60,b'\x5e')
   else:
    value=f['kind']
    if f['mutation']:u.mem_write(D+64,struct.pack('<I',181));u.mem_write(B+44,struct.pack('<4H',1,2,3,4))
   u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,0x76543210);u.reg_write(UC_ARM_REG_R3,0xdeadbeef);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,f in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={**f,'trace':[],'tick_index':0};u.mem_write(D-4,b'\xa5'*76);u.mem_write(B-4,b'\x96'*104);u.mem_write(D+48,bytes([f['initial']]));u.mem_write(D+46,bytes([f['flag']]));u.mem_write(D+52,struct.pack('<II',f['key'],f['last']));u.mem_write(D+60,bytes([f['level']]));u.mem_write(D+64,struct.pack('<I',f['accumulator']))
    for t in range(4):u.mem_write(B+44+t*12,struct.pack('<4H',*f['thresholds'][t*4:t*4+4]))
    for reg,value in [(UC_ARM_REG_R0,f['voltage']),(UC_ARM_REG_R1,f['timestamp']),(UC_ARM_REG_SP,0x2003f000),(UC_ARM_REG_LR,0x20000101)]:u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_charging_cadence'] if candidate else 0x4fe70)|1,0x20000100,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(D-4,76)),bytes(u.mem_read(B-4,104)),states[id(u)]['trace']))
   assert results[0]==results[1],(index,f,[(i,x,y) for i,(x,y) in enumerate(zip(*results)) if x!=y])
   for event in results[0][3]:counts[event[0]]+=1
 vp.write_text(json.dumps(dict(comparisons=len(cases),provider_calls_per_side=counts,native_division_helper_calls=divisions,semantic_arguments=['voltage','charge_start_timestamp'],threshold_bytes=48,threshold_stride=12,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Tick/config endpoints and mutable threshold/state contents are fixtures; native division helper executes, source uses hardware unsigned division','Threshold/runtime state initialization and actual updater/provider composition remain gates','State ordering compared at provider boundaries; interrupt atomicity/timing, full startup and original image identity unproven']),indent=2)+'\n');print('Battery cadence:',len(cases),counts,divisions)
if __name__=='__main__':main()
