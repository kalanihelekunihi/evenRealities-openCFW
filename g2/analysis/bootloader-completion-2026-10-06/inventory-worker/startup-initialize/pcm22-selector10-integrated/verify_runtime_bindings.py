"""Execute stock bytes and independent source leaves; callback bodies controlled."""
from pathlib import Path
import sys,json,hashlib,struct,itertools,importlib.util
from unicorn import *
from unicorn import arm_const as a
ROOT=next(p for p in Path(__file__).resolve().parents if (p/"AGENTS.md").exists())
spec=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py');elf=importlib.util.module_from_spec(spec);spec.loader.exec_module(elf)
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
_,segments,symbols=elf.elf_info(args.elf)
entries={'write':('opencfw_boot_startup_sleep_fields_write',0x41c9ca,0x41ca08),'read':('opencfw_boot_startup_sleep_fields_read',0x41ca0c,0x41ca2c)}
for name,lo,hi in [('20',0x41cdca,0x41cde0),('24',0x41cde0,0x41cdfa),('28',0x41cdfa,0x41ce10),('30',0x41ce10,0x41ce26),('34',0x41ce26,0x41ce3c),('38',0x41ce3c,0x41ce52)]:entries[name]=('opencfw_boot_startup_hook'+name,lo,hi)
entries={'dispatch':('opencfw_boot_startup_spot_dispatch',0x41ce52,0x41d0ee),'trim':('opencfw_boot_startup_trim_version',0x41b918,0x41b954),'info':('opencfw_boot_startup_info_cache',0x41c320,0x41c480)}
trace={}
pointer_map={symbols[n]&~1:o for n,o in [('state_event_dispatch_42d562_native',0x42d562),('state_event_flag_set_42d5c2_native',0x42d5c2),('state_event_finalize_42d5cc_native',0x42d5cc),('autosw_initialize_42d63a_native',0x42d63a),('opencfw_boot_ton_state_event',0x42f38e),('opencfw_boot_ton_trim_cache',0x42f41a),('opencfw_boot_ton_trim_apply',0x42f4b2)]}
pointer_map.update({symbols[n]&~1:o for n,o in [('opencfw_pcm22_post_lptohp',0x42a036),('opencfw_pcm22_timer_service',0x42a04a),('pcm21_boost_service',0x42ae9c),('opencfw_boot_spotmgr_power_state_update_a',0x42a878),('opencfw_boot_spot_state_power_event',0x42ba00)]})
init_map={symbols[n]&~1:o for n,o in [('spotmgr_init_42abbc_native',0x42abbc),('hw_state_compose_42bdf0_native',0x42bdf0),('bl_bl009_dispatch_native',0x42d6c0),('startup_noop_42f670_native',0x42f670)]}
def run(source,name,f):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
 for lo,sz in [(0x410000,0x25000),(0x08000000,0x20000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0xe000e000,0x1000),(0xe001e000,0x1000),(0x40000000,0x100000)]:u.mem_map(lo,sz)
 if source:
  for seg in segments:u.mem_write(seg['address'],seg['data'])
 else:u.mem_write(0x410000,blob)
 def w(p,x):u.mem_write(p,struct.pack('<I',x&0xffffffff))
 w(0xe000ed14,f.get('scr',0));w(0xe001e300,f.get('value',0));u.mem_write(0x20001000,b'\xa5'*4)
 w(0x4002000c,f.get('revision',0));w(0x20000098,f.get('variant',0));w(0x40020028,f.get('seed',0));w(0x40020060,f.get('seed',0));w(0x2002682c,f.get('patch',0));w(0x400201bc,8 if f.get('otp_selected',True) else 0);w(0x40021008,0x08000000 if f.get('otp_power',True) else 0)
  # Deliberately nonzero old slots detect complete table clearing.
 for p in range(0x20026e38,0x20026e74,4):w(p,0xdeadbeef)
 if name!='dispatch':
  for p in range(0x200267f8,0x20026878,4):w(p,0xa5a5a5a5)
 for p in range(0x200271a9,0x200271af):u.mem_write(p,b'\xa5')
 events=[];writes=[];done=False
 def hook(cpu,p,size,_):
  nonlocal done
  if p==0x08000000:done=True;u.emu_stop();return
  if not source and 0x410000<=p<0x435000:trace[p]=bytes(u.mem_read(p,size)).hex()
  if p==(symbols['opencfw_boot_device_mode_wait']&~1 if source else 0x421548):
   space=u.reg_read(a.UC_ARM_REG_R0);offset=u.reg_read(a.UC_ARM_REG_R1);count=u.reg_read(a.UC_ARM_REG_R2);dest=u.reg_read(a.UC_ARM_REG_R3)
   events.append(['INFO',space,offset,count]);status=f.get('failure',0) if offset==f.get('fail_offset',0) else 0
   if not status:
    for i in range(count):w(dest+4*i,f.get('read_value',offset*256+i))
   u.reg_write(a.UC_ARM_REG_R0,status);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if (source and p in init_map) or (not source and p in [0x42abbc,0x42bdf0,0x42d6c0,0x42f670]):
   events.append(['selected-init',hex(init_map[p] if source else p)]);u.reg_write(a.UC_ARM_REG_R0,f.get('status',0));u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR));return
  if p==0x08000100:
   events.append([u.reg_read(a.UC_ARM_REG_R0),u.reg_read(a.UC_ARM_REG_R1)] if name=='24' else ['noarg'])
   u.reg_write(a.UC_ARM_REG_R0,f['status']);u.reg_write(a.UC_ARM_REG_PC,u.reg_read(a.UC_ARM_REG_LR))
 def write(cpu,access,p,size,value,_):writes.append([p,size,value&((1<<(8*size))-1)])
 u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40000000,end=0x400fffff);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0xe000e000,end=0xe001efff)
 u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,0x08000001);u.reg_write(a.UC_ARM_REG_R0,(0 if f.get('null',False) else 0x20001000) if name=='trim' else f.get('arg',0));u.reg_write(a.UC_ARM_REG_R1,f.get('second',0));u.reg_write(a.UC_ARM_REG_PRIMASK,f.get('irq',0))
 pc=(symbols[entries[name][0]]&~1) if source else entries[name][1];u.emu_start(pc|1,0,count=20000);assert done
 table=bytearray(u.mem_read(0x20026e38,60))
 if source:
  for offset in range(0,60,4):
   actual=struct.unpack('<I',table[offset:offset+4])[0]
   aliases=dict(pointer_map,**{})
   aliases.update(init_map)
   if (actual&~1) in aliases:table[offset:offset+4]=struct.pack('<I',aliases[actual&~1]|1)
 return dict(ret=u.reg_read(a.UC_ARM_REG_R0),writes=writes,events=events,output=bytes(u.mem_read(0x20001000,4)).hex(),variant=bytes(u.mem_read(0x20000098,4)).hex(),table=table.hex(),flags=bytes(u.mem_read(0x200271a9,6)).hex(),cache=bytes(u.mem_read(0x200267f8,128)).hex(),irq=u.reg_read(a.UC_ARM_REG_PRIMASK))
fixtures=[]
for rev,var,patch,seed,status in itertools.product([0,32,33,34,35,36,255],[0,1,2,3,4,0xffffffff],[0,1,2,3],[0,0xffffffff],[0,7]):fixtures.append(('dispatch',dict(revision=rev,variant=var,patch=patch,seed=seed,status=status)))
for var,readval,failure,null in itertools.product([0,1,2,3,0xffffffff],[0,1,3,0xffffffff],[0,7],[False,True]):fixtures.append(('trim',dict(variant=var,read_value=readval,fail_offset=0x244,failure=failure,null=null)))
for selected,power,failoffset,failure in itertools.product([False,True],[False,True],[0,0x480,0x204,0x206,0x208,0x210,0x240,0x24a,0x250,0x245],[0,7]):fixtures.append(('info',dict(otp_selected=selected,otp_power=power,fail_offset=failoffset,failure=failure)))
rows=[]
for name,f in fixtures:
 stock=run(False,name,f);source=run(True,name,f)
 if stock!=source:args.output.with_suffix('.failure.json').write_text(json.dumps(dict(name=name,fixture=f,stock=stock,source=source),indent=2));raise AssertionError((name,f,stock,source))
 rows.append(dict(name=name,fixture=f,result=stock))
for p,b in trace.items():assert blob[p-0x410000:p-0x410000+len(bytes.fromhex(b))]==bytes.fromhex(b)
used={p+i for p,b in trace.items() for i in range(len(bytes.fromhex(b)))}
r=dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(blob).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_trace={hex(p):b for p,b in sorted(trace.items())},visited_body_bytes={name:len(used&set(range(lo,hi))) for name,(_,lo,hi) in entries.items()},comparisons=rows,limits=['Native dispatch/trim/cache bodies; INFO read entry and four selected initialization callbacks are explicit synthetic cuts.','Stored table pointers are authenticated original address contracts, not recovered callback implementations or loaded executable fallback in source machine.','No SRAM write hook. Memory-mapped registers, static chip identity and INFO responses are synthetic; no hardware validation.'])
args.output.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(rows),r['visited_body_bytes'])
