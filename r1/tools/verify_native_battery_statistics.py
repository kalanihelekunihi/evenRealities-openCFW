#!/usr/bin/env python3
"""Native charging refresh and zero-filtered trimmed means versus recovered C."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-statistics';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84;B=0x20006890
ENTRIES={'r1_battery_charged_state_refresh':(0x3dd0c,144),'r1_battery_voltage_average':(0x3dda0,80),'r1_battery_level_average':(0x3d834,82)}
P={'osKernelGetTickCount':0x7d28c,'r1_shared_power_client_acquire':0x50778,'r1_battery_charging_progress_reset':0x4fe5c}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_statistics.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 counts={n:0 for n in ENTRIES};rng=random.Random(0x3dda0)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;states={};machines=[];kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];event=(n,);value=0
   if n=='osKernelGetTickCount':
    value=f['tick']
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',0xabcd));u.mem_write(D+44,b'\xff\x00\x03')
   elif n=='r1_shared_power_client_acquire':event+=(u.reg_read(UC_ARM_REG_R0),);assert event[-1]==0
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,device,args=(),tick=0,mutation=False):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'tick':tick,'mutation':mutation};u.mem_write(D-8,b'\x96'*8+bytes(device)+b'\x69'*8);u.mem_write(B-8,b'\xa5'*80);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,v)
    u.mem_write(0x2003f000,struct.pack('<I',args[4] if len(args)>4 else 0))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[name]|1) if candidate else ENTRIES[name][0]|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((None if name=='r1_battery_voltage_average' else u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(D-8,84)),bytes(u.mem_read(B-8,80))))
   assert results[0]==results[1],(name,device,args,tick,mutation,results);counts[name]+=1
  for state,old,counter,tick,voltage,mutation in itertools.product((0,1,2,0xffffffff),(0,1,2,255),(0,1,7,8,255),(0,1,0xffffffff),(0,3800,65535),(False,True)):
   device=bytearray([0x93]*68);device[44]=rng.choice((0,1,50,255));device[45]=old;device[46]=counter;struct.pack_into('<H',device,42,voltage)
   case('r1_battery_charged_state_refresh',device,(state,B+36,B+12,B+40,B+14),tick,mutation)
  for name,width,offset in [('r1_battery_level_average',1,34),('r1_battery_voltage_average',2,18)]:
   maximum=(1<<(width*8))-1
   for mask,pattern in itertools.product(range(256),range(4)):
    values=[(1 if pattern==0 else maximum if pattern==1 else (i+1)*(maximum//9) if pattern==2 else (1 if i%2 else maximum)) if mask&(1<<i) else 0 for i in range(8)];device=bytearray([0x93]*68)
    for i,v in enumerate(values):device[offset+i*width:offset+(i+1)*width]=v.to_bytes(width,'little')
    case(name,device)
   for _ in range(1024):
    device=bytearray(rng.randbytes(68))
    for i in range(8):device[offset+i*width:offset+(i+1)*width]=rng.choice((0,rng.randrange(maximum+1))).to_bytes(width,'little')
    case(name,device)
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},entries=ENTRIES,application_linked=False,instruction_identity=False,limitations=['Tick, shared-resource acquire and charging-progress reset are fixtures','Raw device/runtime addresses are fixture storage; initialization and atomicity remain gates','Level trimmed mean rounds with+3 before divide6; voltage trimmed mean truncates; all-zero voltage leaves prior value','Actual updater/statistics composition is a separate receipt']),indent=2)+'\n');print('Battery statistics:',counts)
if __name__=='__main__':main()
