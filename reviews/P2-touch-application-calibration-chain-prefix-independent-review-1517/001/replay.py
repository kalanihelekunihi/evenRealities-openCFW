from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-application-calibration-chain-prefix-independent-review-1517/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();lit={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x3ea4,0x3ec4,4)};rows=[]
for failure in [0]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x200004c0,d[0x828c:0x8650]);u.mem_map(0x40000000,0x100000);u.mem_map(0x40100000,0x1000);u.mem_map(0x40250000,0x1000);u.mem_map(0x40290000,0x10000);u.mem_map(0xe000e000,0x1000);u.mem_write(0x20000400,d[:192]);u.mem_write(0xe000ed08,(0x20000400).to_bytes(4,'little'));u.mem_map(0x0ffff000,0x1000);u.mem_write(0x0ffff1cc,bytes((i*5+9)&255 for i in range(64)));u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_PRIMASK,1);calls=[];writes=[];pcs=[];actual_args=[]
 driver_calls=[0x45d0,0xa148,0x9fd4,0xa104,0xa148,0xa01c,0xa104,0xa148,0xa01c,0xa104,0xa0bc]+[0x8ee4]*6+[0x45a4]
 driver_calls=[x for x in driver_calls if x not in [0xa148,0xa104,0x9fd4,0xa01c,0xa0bc]]
 driver_calls=[0xa33c,0x9c80,0x9f44,0x4734,0xa188,0x9c80,0x9f44,0xa33c,0x4734]
 driver_calls=[x for x in driver_calls if x not in [0xa33c,0x4734,0xa188,0x9f44,0x9c80]]
 targets=driver_calls+[0x8a38,0x8a78,0x8ae0,0x8aac,0x6078,0x60ea,0x6044,0x8fd0,0x7064,0x6a80,0x9178,0x7288,0x5fa4,0x9178,0x7288,0x5fa4,0x9178,0x7288,0x5fa4,0x5ca2,0x7bb8,0x5c7a,0x5fa4,0x5c8e,0x5c02,0x5c02,0x5c02,0x4f54,0x4e1c,0x5dd8,0x5d90]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x3ee0:actual_args.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]])
  if p in [0x3cc6,0x3d50]:u.emu_stop();return
  if p in targets:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append(dict(pc=p,args=args));u.reg_write(UC_ARM_REG_R0,failure if p==0x44c4 else 1 if p==0x5fa4 else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x3cb5,0,count=1000000)
 assert u.reg_read(UC_ARM_REG_SP)==0x2000eff8
 if failure:assert u.reg_read(UC_ARM_REG_PC)==0x3cc6 and [x['pc'] for x in calls]==targets[:2] and u.reg_read(UC_ARM_REG_PRIMASK)==1
 else:
  assert u.reg_read(UC_ARM_REG_PC)==0x3d50 and [x['pc'] for x in calls]==targets and u.reg_read(UC_ARM_REG_PRIMASK)==0
  assert actual_args[0]==[lit[0x3eac],lit[0x3ea8],lit[0x3ea4]]
  assert [lit[0x3eb0],1,1] in writes and [lit[0x3eb4],4,640] in writes
  assert [w for w in writes if w[0]==lit[0x3eb8]+64][-2:]==[[lit[0x3eb8]+64,4,1],[lit[0x3eb8]+64,4,2]]
  assert calls[-2]['args'][0]==lit[0x3ebc] and calls[-1]['args'][:2]==[lit[0x3ec0],lit[0x3ebc]]
 assert int.from_bytes(u.mem_read(0x20000f38,4),'little')==0x200004cc
 assert [w for w in writes if w[0]==0x40010104]==[[0x40010104,4,65]]
 for address in [0x40010400,0x40010500]:assert [w for w in writes if w[0]==address]==[[address,4,0x3300],[address,4,0x3318]]
 assert [w for w in writes if w[0]==0x40010304]==[[0x40010304,4,0x300]]
 assert [w for w in writes if w[0]==0x40010000]==[[0x40010000,4,v] for v in [0x40000041,0x8000ff41,0x40000080,0x8000ff80,0x400000c0,0x8000ffc0]]
 rows.append(dict(actual_3ee0_args=actual_args,failure=failure,stop_pc=u.reg_read(UC_ARM_REG_PC),calls=calls,writes=writes,pcs=pcs,primask=u.reg_read(UC_ARM_REG_PRIMASK)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');assert int.from_bytes(u.mem_read(0x20000878,4),'little')==48000000
assert int.from_bytes(u.mem_read(0x20000874,4),'little')==48000
assert u.mem_read(0x20000870,1)==bytes([48])
assert int.from_bytes(u.mem_read(0x2000086c,4),'little')==((48000<<15)&0xffffffff)
assert int.from_bytes(u.mem_read(0x200008e8,4),'little')==0
assert int.from_bytes(u.mem_read(0x20000f40,4),'little')==0x35e5
assert u.mem_read(0x20000f44,16)==bytes(16)
assert int.from_bytes(u.mem_read(0x2000043c,4),'little')==0xa5f5
assert int.from_bytes(u.mem_read(0xe000e010,4),'little')==3
assert int.from_bytes(u.mem_read(0xe000e014,4),'little')==40
assert int.from_bytes(u.mem_read(0xe000e018,4),'little')==0
assert u.mem_read(0x200009d0,8)==bytes.fromhex('554e56450000e803')
assert [c['pc'] for c in calls[:4]]==[0x8a38,0x8a78,0x8ae0,0x8aac]
assert u.mem_read(0x20000940,80)==(1000).to_bytes(2,'little')+bytes(78)
assert int.from_bytes(u.mem_read(0x200004cc+16,4),'little')==0
assert int.from_bytes(u.mem_read(0x200004cc+20,4),'little')==0x20000850
assert int.from_bytes(u.mem_read(0x20000850+16,4),'little')==0x200004cc
assert int.from_bytes(u.mem_read(0x20000850+20,4),'little')==0
assert int.from_bytes(u.mem_read(0x200008ec+0x44,4),'little')==0x3701
assert int.from_bytes(u.mem_read(0x40250000,4),'little')==0x80000100
assert int.from_bytes(u.mem_read(0xe000e100,4),'little')==256
assert int.from_bytes(u.mem_read(0xe000e280,4),'little')==256
assert int.from_bytes(u.mem_read(0x2000045c,4),'little')==0x3625
assert 0xa214 in pcs and 0xa274 in pcs
assert [int.from_bytes(u.mem_read(0x200008ec+x,4),'little') for x in [0x28,0x2c,0x30,0x34,0x38,0x3c,0x40]]==[0x200009b0,16,0,0,0x200009a0,16,0]
assert int.from_bytes(u.mem_read(0x20000460,4),'little')==0x3949
assert [w for w in writes if w[0]==0xe000e100]==[[0xe000e100,4,128],[0xe000e100,4,256]]
assert 0x4c7c in pcs and 0x4c72 in pcs
assert 0x4c44 in pcs and 0x8fa0 in pcs
descriptor=0x200004ec
context=int.from_bytes(u.mem_read(descriptor+8,4),'little')
assert u.mem_read(context+0x55,1)==bytes([1]) and u.mem_read(context+0x73,1)==bytes([0])
assert pcs.count(0x6ac0)==9
assert pcs.count(0x6ac0)==9
assert u.mem_read(context+0x76,1)==bytes([1])
assert 0x7d92 in pcs
assert pcs.count(0x5868)==3
assert 0x5d70 in pcs
scaled_input=int.from_bytes(u.mem_read(context+0x24,4),'little')
scaled_factor=int.from_bytes(u.mem_read(context+0x2c,4),'little')
scaled=((scaled_input*scaled_factor)&0xffffffff)>>14
assert int.from_bytes(u.mem_read(context+0x28,4),'little')==(0 if scaled==0 else min(scaled-1,65535))
assert 0x6384 in pcs
assert 0x5378 in pcs
assert 0x52bc in pcs
output=int.from_bytes(u.mem_read(descriptor+36,4),'little')
assert bytes(u.mem_read(output+144,28))==d[0xb470-0x3300:0xb48c-0x3300]
assert 0x50e4 in pcs
print("MAP",bytes(u.mem_read(context+98,20)).hex())
assert u.mem_read(context+98,1)==bytes([2])
assert u.mem_read(context+99,1)==bytes([255])
assert u.mem_read(context+104,1)==bytes([0])
assert u.mem_read(context+107,1)==bytes([1])
assert pcs.count(0x56a4)==2
assert 0x5548 in pcs and 0x51bc in pcs and 0x5188 in pcs
assert pcs.count(0x7dde)==3
assert pcs.count(0x5cac)==3
assert pcs.count(0x7bc0)==3
assert pcs.count(0x6928)==3 and pcs.count(0x6980)==3
(o/'pseudocode.md').write_text('# Startup with original calibration chain\n\nOriginal7BC0 now executes for three rows, with original6AC0 state transitions,6928 setup and6980 completion. Remaining controls are6A80 state5 dependency,9178 scratch/peripheral helper,7288 acquisition, and5FA4 budget. The latter returns1, allowing the modeled ready bit in the setup register to produce a nonzero remaining countdown. All other boundary responses remain zero.\n\nThe inherited startup assertions and exact remaining call sequence check nine state-helper entries,three calibration/setup/completion entries and arrival at3D50. Inputs use authenticated initialized configuration;MMIO/externalclocktables remain synthetic. Physical acquisition, scratch helper effects andwhole-firmware coverage remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),literals={hex(a):hex(v) for a,v in lit.items()},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS startup success and breakpoint-reach prefixes')
