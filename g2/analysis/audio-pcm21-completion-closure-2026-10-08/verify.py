from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];sys.path.insert(0,str(R/'g2/analysis/audio-platform-callbacks-closure-2026-10-08'))
from itcm_record import decode_itcm
from startup_evidence import initialized_record
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];itcm=decode_itcm(raw);startup=initialized_record(raw)
elf=Path('/tmp/opencfw-pcm21-completion/control.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def w(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0x40008000,0x1000),(0x40004000,0x1000),(0xe000e000,0x2000),(0xe001e000,0x1000),(0x47ff0000,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 w(u,0xe000ed88,0xf00000);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);return u

def run(native,action,enable,metadata,old_cpu,gate=3,signature=0x1f01600d,mask=0,profile=3,ton=6,powerflags=0,dev=0x40000,aud=0x80,temp=2,otherflags=0,stop_apply=False):
 u=machine();w(u,0x40021108,gate<<4);w(u,0x2005665c,signature);w(u,0x200742b0,powerflags);w(u,0x20000294,profile);w(u,0x2000029c,ton);w(u,0x20000298,profile)
 for a,v in [(0x40021008,dev),(0x40021010,aud),(0x40021018,0x12345678),(0x40021028,0x87654321),(0x400204e8,0x140)]:w(u,a,v)
 u.mem_write(0x20074f60,b'\0'*32);u.mem_write(0x20074f6d,bytes([otherflags]));u.mem_write(0x20074f75,bytes([temp,old_cpu]));u.mem_write(0x20004539,b'\xa5')
 for i in range(20):w(u,0x20056660+i*4,(0x01040608+i*0x0102040b)&0xffffffff)
 m=0 if metadata is None else 0x20006000;w(u,0x20006000,0 if metadata is None else metadata);w(u,0x20006004,0xa5a5a5a5);w(u,0x20006008,0xa5a5a5a5)
 calls=[];writes=[];boundary=[];plans=[]
 def hook(u,a,n,d):
  if native:a={sym["pcm21_prepare"]&~1:0x5a0c20,sym["pcm21_change_state"]&~1:0x5a0d44,sym["pcm21_plan"]&~1:0x5a13e8,sym["pcm21_apply"]&~1:0x5a0fc4}.get(a,a)
  if a==0x5a13e8:plans.append(bytes(u.mem_read(u.reg_read(UC_ARM_REG_R0),19)).hex())
  if a in [0x5a0c20,0x5a0d44,0x5a13e8,0x5a0fc4]:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
   if a in [0x5a0c20,0x5a13e8]:args=[bytes(u.mem_read(args[0],19)).hex()]
   if a==0x5a0d44:args=args[:2]
   calls.append([hex(a),args])
   if a==0x5a0fc4 and stop_apply:boundary.append([hex(a),args]);u.emu_stop()
 def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook)
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 u.reg_write(UC_ARM_REG_R0,action);u.reg_write(UC_ARM_REG_R1,enable);u.reg_write(UC_ARM_REG_R2,m);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 try:u.emu_start((sym['pcm21_control'] if native else 0x5a1738)|1,0x2007f000,count=500000)
 except UcError as e:raise AssertionError(('runtime',native,action,metadata,old_cpu,hex(u.reg_read(UC_ARM_REG_PC)),e))
 assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',native,action,metadata,old_cpu,hex(u.reg_read(UC_ARM_REG_PC)))
 return dict(return_value=None if boundary else u.reg_read(UC_ARM_REG_R0),calls=calls,plans=plans,writes=writes,boundary=boundary,globals=bytes(u.mem_read(0x20074f60,32)).hex(),selected_profile_ton=[word(u,0x20000294),word(u,0x2000029c)],metadata=bytes(u.mem_read(0x20006000,12)).hex(),temperature_flag=bytes(u.mem_read(0x20004539,1)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[];cases=[]
for gate,sig,action,m,mask in itertools.product([0,1,2,3],[0,0x1f01600d],[0,2,7],[None,0],[0,1]):
 if gate==3 and sig==0x1f01600d:continue
 cases.append(dict(action=action,enable=1,metadata=m,old_cpu=2,gate=gate,signature=sig,mask=mask))
for action,enable,m,old,mask in itertools.product([0,1,2,3,4,5,6,7,256,259],[0,1],[None,0,1,2,3,4],[0,1,2,3,4],[0,1]):
 cases.append(dict(action=action,enable=enable,metadata=m,old_cpu=old,mask=mask))
for bits in [0xc3960000,0xc3888000,0xc1b00000,0xc1a00000,0xc0000000,0xbf800000,0,0x42400000,0x42480000,0x447a0000,0x7fc00000,0x7f800000,0xff800000]:cases.append(dict(action=2,enable=1,metadata=bits,old_cpu=0))
# Targeted profile/flag fixtures exercise branches omitted by the base matrix.
for profile,powerflags,dev,aud in itertools.product([3,8,12],[0,1],[0,0x40000],[0,0x80,0x4c4]):
 cases.append(dict(action=0,enable=1,metadata=2,old_cpu=0,profile=profile,powerflags=powerflags,dev=dev,aud=aud))
for flag in [0,1]:
 cases.append(dict(action=0,enable=1,metadata=2,old_cpu=1,otherflags=flag))
# Derive an unchanged-plan fixture from the actual stock planner, never a stub.
deferred=dict(action=0,enable=1,metadata=0,old_cpu=1)
changed=run(False,**deferred)
assert bytes.fromhex(changed['globals'])[0x16]==0 and any(c[0]=='0x5a0fc4' for c in changed['calls'])
pair=changed['selected_profile_ton'];same=dict(**deferred,profile=pair[0],ton=pair[1]);unchanged=run(False,**same)
assert bytes.fromhex(unchanged['globals'])[0x16]==1 and not any(c[0]=='0x5a0fc4' for c in unchanged['calls'])
cases.append(same)
for old in [2,3,4]:
 for target in [0,1]:
  fixture=dict(action=0,enable=1,metadata=target,old_cpu=old)
  actual=run(False,**fixture);assert actual['calls']==[] and bytes.fromhex(actual['globals'])[0x16]==target
# Inactive SIMObuck returns before both metadata outputs and temperature state.
for gate in [0,1,2]:
 actual=run(False,action=2,enable=1,metadata=0x42480000,old_cpu=0,gate=gate)
 assert actual['metadata']=='00004842a5a5a5a5a5a5a5a5' and actual['temperature_flag']=='a5' and bytes.fromhex(actual['globals'])[0x15]==2
for case in cases:
 o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['All four PCM2.1 children are reconstructed; common TON/timer/cache providers execute original instructions.','Synthetic calibration and passive MMIO/IRQ/cache state. Full RTOS/physical timing not established.','New control plus sealed first-party classifier; profiling stack-only NOP log records omitted.','Selected M33-compatible M55 instruction subset.']),separators=(',',':'))+'\n');print('PASS',len(rows),'PCM2.1 control comparisons')
