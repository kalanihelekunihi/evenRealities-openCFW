#!/usr/bin/env python3
"""Compare event/BL009 callback region against fixed-address C in Unicorn."""
from pathlib import Path
import hashlib, importlib.util, json, struct
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn import arm_const as a

ROOT=Path(__file__).resolve().parents[5]; HERE=Path(__file__).resolve().parent
IMAGE=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
EXPECTED='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
sp=importlib.util.spec_from_file_location('elf',ROOT/'g2/components/bootloader/update_core/elf_reader.py')
elf=importlib.util.module_from_spec(sp);sp.loader.exec_module(elf)
blob=IMAGE.read_bytes(); image_sha=hashlib.sha256(blob).hexdigest();assert image_sha==EXPECTED
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
ELF=args.elf;_,segments,symbols=elf.elf_info(ELF)
STOP=0x08000000; DATA=0x20001000
SYMS={'count':'event_test_event_count','log':'event_test_event_log'}
ENTRIES={
 '42d562':(0x42d562,'state_event_dispatch_42d562_native',0x42d5c2),
 '42ced8':(0x42ced8,'state_range_update_42ced8_native',0x42cfe0),
 '42cfe0':(0x42cfe0,'state_event_zero_42cfe0_native',0x42d0f2),
 '42d104':(0x42d104,'state_event_one_value_42d104_native',0x42d3bc),
 '42d3bc':(0x42d3bc,'state_register_initialize_42d3bc_native',0x42d562),
 '42cea4':(0x42cea4,'state_update_critical_42cea4_native',0x42ced8),
 '42cdf8':(0x42cdf8,'state_adjust_42cdf8_native',0x42cea4),
 '41f3f0':(0x41f3f0,'power_predicate_41f3f0_native',0x41f424),
 '42d5c2':(0x42d5c2,'state_event_flag_set_42d5c2_native',0x42d5cc),
 '42d5cc':(0x42d5cc,'state_event_finalize_42d5cc_native',0x42d5f8),
 '42d63a':(0x42d63a,'autosw_initialize_42d63a_native',0x42d692),
}
MMIO=[0x40008010]+[0x40008200+i*0x20 for i in range(16)]+[
 0x40008800,0x4002000c,0x40020044,0x4002004c,0x40020080,0x40020088,
 0x400201b0,0x40020344,0x4002034c,0x40020354,0x40020358,0x40020380,
 0x40021004,0x40021108,0x400211a0,0x400211a4,0x400211a8,0x400211ac,0x400211b4,0x400211bc]
def u32(v):return struct.pack('<I',v&0xffffffff)
def get32(u,p):return struct.unpack('<I',u.mem_read(p,4))[0]
def put32(u,p,v):u.mem_write(p,u32(v))

def setup(u,source,f):
    for p,sz in [(0,0x1000),(0x410000,0x25000),(STOP,0x1000),(0x10000,0x10000),(0x30000,0x10000),(0x20000000,0x40000),(0x40000000,0x100000),(0xe000e000,0x2000)]:u.mem_map(p,sz)
    if source:
        for s in segments:u.mem_write(s['address'],s['data'])
    else:u.mem_write(0x410000,blob)
    put32(u,0xe000ed88,0x00f00000)
    for p in MMIO:put32(u,p,0x5a5a0000|(p&0xffff))
    put32(u,0x40021108,f.get('mode_reg',0))
    put32(u,0x40021004,f.get('trim_control',0))
    put32(u,0x40008800,f.get('power_mode',0))
    put32(u,0x40008010,f.get('active_mask',0))
    for i,v in enumerate(f.get('channel_words',[0]*16)):put32(u,0x40008200+i*0x20,v)
    ram_init={0x200271ac:f.get('event_enable',0),0x200271b3:f.get('flag3',0),
      0x200271a8:f.get('state_enable',0),
      0x200271b4:f.get('flag4',0),0x200271b6:f.get('flag6',0),
      0x200271b7:f.get('flag7',0),0x200271b8:f.get('event_state',0),
      0x200271b9:f.get('event_type',f.get('event_adjust',0)),0x200271bc:f.get('critical_lock',0),
      0x200271bf:f.get('predicate',0),
      0x200271c0:f.get('event_result',0),0x2002709c:f.get('saved_cpu',0),
      0x20027098:f.get('saved_mode',0),0x200270a0:f.get('saved_state',0)}
    for p,v in ram_init.items():u.mem_write(p,bytes([v&255])) if p>=0x200271a0 else put32(u,p,v)
    fl=f.get('floats',(0.0,0.0,0.0));u.mem_write(DATA,struct.pack('<fff',*fl))
    put32(u,0x20027050,f.get('trim_base',0))
    u.mem_write(DATA+0x100,bytes(f.get('state_bytes',[0,0,0,0])))
    return

def run(source,key,f):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33);setup(u,source,f)
    events=[];writes=[];trace={};done=[False]
    def ev(kind,arg):events.append([kind,arg&0xffffffff])
    def hook(cpu,pc,size,_):
        if pc==STOP:done[0]=True;cpu.emu_stop();return
        if 0x410000<=pc<0x435000:trace[pc]=bytes(cpu.mem_read(pc,size)).hex()
        if (not source and pc==0x41d1c0) or (source and pc==(symbols['opencfw_boot_delay_us_math']&~1)):ev(3,cpu.reg_read(a.UC_ARM_REG_R0))
        if pc==0x40:
            cycles=cpu.reg_read(a.UC_ARM_REG_R0)
            ev(5,cycles)
            cpu.reg_write(a.UC_ARM_REG_PC,cpu.reg_read(a.UC_ARM_REG_LR));return
    def wr(cpu,access,p,size,value,_):
        if p>=0x40000000:writes.append([p,size,value&((1<<(8*size))-1)])
    u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr,begin=0x40000000,end=0x400fffff)
    u.reg_write(a.UC_ARM_REG_SP,0x2003f000);u.reg_write(a.UC_ARM_REG_LR,STOP|1)
    u.reg_write(a.UC_ARM_REG_FPEXC,0x40000000)
    if key=='42d562':
        selector=f.get('selector',0)
        stateptr=f.get('state_ptr',DATA if (selector&255)==2 else DATA+0x100)
        u.reg_write(a.UC_ARM_REG_R0,selector);u.reg_write(a.UC_ARM_REG_R1,f.get('unused',0xdeadbeef));u.reg_write(a.UC_ARM_REG_R2,stateptr)
        entry=ENTRIES[key][0] if not source else symbols[ENTRIES[key][1]]&~1
    else:
        entry=ENTRIES[key][0] if not source else symbols[ENTRIES[key][1]]&~1
        if key=='42ced8':u.reg_write(a.UC_ARM_REG_R0,DATA)
        elif key=='42d104':u.reg_write(a.UC_ARM_REG_R0,f.get('value',1))
    u.emu_start(entry|1,0,count=20000);assert done[0],(key,f,'not returned',hex(u.reg_read(a.UC_ARM_REG_PC)))
    watched=MMIO+[0x4002004c,0x40020044,0x2002709c,0x20027098,0x200270a0]
    # Deduplicate watched addresses while preserving order.
    watched=list(dict.fromkeys(watched))
    result={'ret':u.reg_read(a.UC_ARM_REG_R0),'events':events,'mmio_writes':writes,
      'mmio_state':[[p,get32(u,p)] for p in watched],
      'ram_state':bytes(u.mem_read(0x200271a8,0x20)).hex(),
      'other_state':bytes(u.mem_read(0x20027090,0x20)).hex(),
      'float_state':bytes(u.mem_read(DATA,12)).hex(),
      'primask':u.reg_read(a.UC_ARM_REG_PRIMASK)}
    return result,trace

fixtures=[]
# Parent dispatcher covers ignored selectors and all four selected operations.
for f in [
 {'selector':0,'state_bytes':[2,0,0,0],'event_enable':1,'event_type':0,'event_result':0},
 {'selector':0,'state_bytes':[2,0,0,0],'event_enable':1,'event_type':2,'event_result':0},
 {'selector':0,'state_bytes':[2,0,0,0],'event_enable':0},
 {'selector':0,'state_bytes':[0,0,0,0],'event_enable':1},
 {'selector':1,'state_bytes':[0,0,0,0],'mode_reg':0x30,'flag3':0,'flag4':0},
 {'selector':1,'state_bytes':[0,0,0,0],'mode_reg':0x20,'flag3':1,'flag4':1},
 {'selector':1,'state_bytes':[1,0,0,0],'mode_reg':0x30,'flag3':0,'flag4':0},
 {'selector':1,'state_bytes':[2,0,0,0],'mode_reg':0x30,'flag3':1,'flag4':1},
 {'selector':1,'state_bytes':[1,0,0,0],'mode_reg':0x20,'flag3':1,'flag4':1},
 {'selector':2,'floats':(-300.,0.,0.)}, {'selector':2,'floats':(-273.,0.,0.)},
 {'selector':2,'floats':(-100.,0.,0.)}, {'selector':2,'floats':(35.,0.,0.)},
 {'selector':2,'floats':(40.,0.,0.)}, {'selector':2,'floats':(50.,0.,0.)},
 {'selector':2,'floats':(60.,0.,0.)}, {'selector':2,'floats':(1000.,0.,0.)},
 {'selector':3,'state_bytes':[1,0,0,0]}, {'selector':4,'state_bytes':[1,0,0,0]},
 {'selector':5,'state_bytes':[1,0,0,0]}, {'selector':6,'state_bytes':[1,0,0,0]},
 {'selector':7,'state_bytes':[1,0,0,0]},
 {'selector':0x101,'state_bytes':[1,0,0,0]},
]:fixtures.append(('42d562',f))
# Exact float32 threshold neighbors plus signed zero, NaN, and infinities.
def f32bits(bits):return struct.unpack('<f',struct.pack('<I',bits))[0]
for x in [f32bits(0xc3888001),-273.0,f32bits(0xc3887fff),
          f32bits(0x420bffff),35.0,f32bits(0x420c0001),
          f32bits(0x4247ffff),50.0,f32bits(0x42480001),
          f32bits(0x4479ffff),1000.0,f32bits(0x447a0001),
          0.0,-0.0,float('nan'),float('inf'),float('-inf')]:
    fixtures.append(('42d562',{'selector':2,'floats':(x,0.,0.)}))
    fixtures.append(('42ced8',{'floats':(x,0.,0.)}))
# Exercise the zero-event scan's valid/invalid encoded channels and power branches.
for pred,power,enabled,kind,active,code in [
 (0,0,1,0,1,5),(0,0,1,0,1,10),(0,0,1,0,1,20),(0,0,1,0,1,300),
 (1,1,1,0,0,0),(0,1,1,2,0,0),(0,3,1,0,0,0)]:
 words=[0]*16
 if active:words[0]=1|(code<<8)
 fixtures.append(('42cfe0',dict(predicate=pred,power_mode=power,event_enable=enabled,event_type=kind,
   active_mask=active,channel_words=words)))
# Direct range and register callback entries; parent cases also cover these.
for k in ('42d5c2','42d5cc','42d63a'):
 fixtures.append((k,{'flag7':1,'event_adjust':2,'critical_lock':0,'state_enable':1,'mode_reg':0x30}))
for state,correction in [(0,False),(1,False),(2,False),(0,True),(2,True)]:
 fixtures.append(('42d562',{'selector':2,'floats':(40.,0.,0.),'event_enable':1,
   'state_enable':1,'mode_reg':0x30,'trim_base':64,'flag4':1,
   'trim_control':(1<<18) if correction else 0,'event_adjust':state}))

rows=[];stock_traces={}
for key,f in fixtures:
    orig,trace=run(False,key,f);src,_=run(True,key,f)
    if orig!=src:
        args.output.with_suffix('.failure.json').write_text(json.dumps({'entry':key,'fixture':f,'stock':orig,'source':src,'trace':{hex(p):b for p,b in sorted(trace.items())}},indent=2)+'\n')
        raise SystemExit(f'MISMATCH {key} {f}: {orig} != {src}')
    rows.append({'entry':key,'fixture':f,'result':orig,
      'stock_entry_points_visited':[hex(v[0]) for v in ENTRIES.values() if v[0] in trace]})
    stock_traces.update(trace)

extents={k:(v[0],v[2]) for k,v in ENTRIES.items()}
# Include dispatcher-selected descendants in visited-byte accounting.
for k in ('42ced8','42cfe0','42d104','42d3bc','42d562','42cea4','42cdf8','41f3f0'):
 start,end=extents[k];seen={p+i for p,b in stock_traces.items() for i in range(len(bytes.fromhex(b))) if start<=p<end}
 extents[k]=(start,end,len(seen))
for k in ('42d5c2','42d5cc','42d63a'):
 start,end=extents[k];seen={p+i for p,b in stock_traces.items() for i in range(len(bytes.fromhex(b))) if start<=p<end}
 extents[k]=(start,end,len(seen))
out={'status':'PASS','cases':len(rows),'locked_image_sha256':image_sha,
 'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'linked_native_sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'g2/components/bootloader/platform_startup/delay_math.S',ROOT/'g2/components/bootloader/platform_control/critical_save.S']},
 'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'extents_and_coverage':{k:{'start':hex(v[0]),'end_exclusive':hex(v[1]),'visited':v[2],
   'extent_bytes':v[1]-v[0]} for k,v in extents.items() if len(v)==3},
 'comparisons':rows,'stock_instruction_trace':{hex(p):b for p,b in sorted(stock_traces.items())},
 'limits':['Linked native sources: platform_startup/delay_math.S and platform_control/critical_save.S. The resident ROM cycle routine at Thumb address 0x40 is the only delay-chain cut; its input cycle count is logged, then it returns immediately. No elapsed-time or clock-accuracy claim.','Synthetic MMIO/RAM values only; no physical peripheral claims.','42cea4, 42cdf8, 41f3f0, critical-save and delay math execute natively in both the locked image and compiled C.','The standalone compiled C is analysis evidence, not integrated firmware or byte-equivalence proof.']}
args.output.write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),out['extents_and_coverage'])
