from pathlib import Path
import sys,struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];previous=R/'g2/analysis/audio-platform-callbacks-closure-2026-10-08';sys.path.insert(0,str(previous))
from itcm_record import decode_itcm
from startup_evidence import initialized_record
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];itcm=decode_itcm(raw);startup=initialized_record(raw)
elf=Path('/tmp/opencfw-transition-producers/producers.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def w(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0x40008000,0x1000),(0x40004000,0x1000),(0xe000e000,0x2000),(0x47ff0000,0x1000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 w(u,0xe000ed88,0xf00000);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);return u
entries={'stop':(0x4802ce,'pcm22_timer_stop'),'complete2':(0x5a23f8,'pcm22_sequence_2_complete'),'complete7':(0x5a2b14,'pcm22_sequence_7_complete'),'dispatch':(0x5a40ca,'pcm22_boost_completion'),'start2':(0x5a22c0,'pcm22_sequence_2'),'complete21':(0x5a3e24,'pcm22_sequence_21_complete'),'post':(0x5a40b6,'pcm22_post_low_to_high')}
def run(native,kind,sequence=2,initial=0,clock=0,ready=0,cache=0,mask=0,next=1,old=5,ton=0,trim=0,enabled=0,intstat=0,continue_flag=1,clock_clients=0,clock_allowed=0):
 u=machine()
 for a in [0x40020044,0x4002004c,0x40020080,0x4002037c,0x40020344,0x40020358,0x400083e0,0x40008010,0x40008068]:w(u,a,initial)
 w(u,0x400083e0,(initial&~1)|enabled);w(u,0x40008064,intstat);w(u,0x40021000,clock);w(u,0x40004044,cache);w(u,0x40004030,ready);w(u,0x400204e8,0x140)
 u.mem_write(0x20004536,bytes([clock_allowed]));w(u,0x20073348,clock_clients);u.mem_write(0x20004540,bytes([sequence]));u.mem_write(0x20074f60,b'\xa5'*32);u.mem_write(0x20074f77,bytes([continue_flag]));w(u,0x200002a0,next)
 for a,v in [(0x200742d4,trim&127),(0x200742d8,(trim>>7)&127),(0x200742dc,(trim>>14)&1023),(0x200742e0,(trim>>24)&15)]:w(u,a,v)
 for i in range(20):w(u,0x20056660+i*4,(trim+(i*0x0212048b))&0xffffffff)
 w(u,0x200566ac,trim);w(u,0x200566b0,trim);w(u,0x200566b4,trim);w(u,0x200566b8,trim);w(u,0x200566bc,trim)
 writes=[];calls=[]
 def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 def hook(u,a,n,d):
  if a==sym['pcm22_ton_adjust']&~1:calls.append(['0x5a423c',u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
  if a in [0x4807a0,0x480240,0x4c4530,0x5a423c,0x4807fc]:calls.append([hex(a),*[u.reg_read(r) for r in ([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3] if a==0x4807fc else [UC_ARM_REG_R0,UC_ARM_REG_R1] if a in [0x4c4530,0x5a423c] else [UC_ARM_REG_R0])]])
 u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_PRIMASK,mask)
 for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[next,old,ton,0xabcdef01]):u.reg_write(reg,v)
 entry=sym[entries[kind][1]] if native else entries[kind][0];u.emu_start(entry|1,0x2007f000,count=500000)
 assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,(kind,hex(u.reg_read(UC_ARM_REG_PC)))
 if kind=='post':assert u.reg_read(UC_ARM_REG_R0)==0
 return dict(continuation_flag=bytes(u.mem_read(0x20074f77,1)).hex(),writes=writes,calls=calls,trim_globals=bytes(u.mem_read(0x200742d4,24)).hex(),sequence=bytes(u.mem_read(0x20004540,1)).hex(),last_state=word(u,0x200002a4),clock_clients=bytes(u.mem_read(0x20073324,56)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[];cases=[]
for kind,initial,trim,mask in itertools.product(['stop','complete2'],[0,0xa5a5a5a5,0xffffffff],[0,0x12345678,0xffffffff],[0,1]):cases.append(dict(kind=kind,initial=initial,trim=trim,mask=mask))
for kind,seq,clock,ready,cache,mask in itertools.product(['complete7','dispatch'],[0,2,7,26],[0,1,2,6],[0,0x1000000],[0,0x20],[0,1]):
 if kind=='complete7' and seq!=7:continue
 cases.append(dict(kind=kind,sequence=seq,clock=clock,ready=ready,cache=cache,mask=mask,initial=0xa5a5a5a5,trim=0x89abcdef))
for next,old,ton,trim,mask,enabled,intstat,seq in itertools.product([0,1,8,19],[0,5,19],[0,7],[0,0x12345678,0xffffffff],[0,1],[0,1],[0,0x40000000],[2,7,26]):
 if not enabled and (intstat or seq!=26):continue
 cases.append(dict(kind='start2',next=next,old=old,ton=ton,trim=trim,mask=mask,enabled=enabled,intstat=intstat,sequence=seq,clock=0,ready=0x1000000,cache=0x20))
for kind,next,trim,flag in itertools.product(['complete21','post'],[0,1,8,19],[0,0x12345678,0xffffffff],[0,1,255]):
 cases.append(dict(kind=kind,next=next,trim=trim,continue_flag=flag,initial=0xa5a5a5a5))
for kind,clients,initial,mask,sequence in itertools.product(['stop','dispatch'],[0,0x20000,0x20001],[0,0xa5a5a5a5],[0,1],[2,7,26]):
 cases.append(dict(kind=kind,clock_clients=clients,initial=initial,mask=mask,sequence=sequence,trim=0x12345678,clock=0))
for next,ton,mask,enabled in itertools.product([0,8],[0,7],[0,1],[0,1]):
 cases.append(dict(kind='start2',next=next,old=5,ton=ton,mask=mask,enabled=enabled,sequence=2,trim=0x12345678,clock_allowed=1))
for case in cases:
 o=run(False,**case);n=run(True,**case);assert o==n,(case,o,n);rows.append(dict(inputs=case,**o))
(D/'previous-functions-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Synthetic calibration/trim words and passive MMIO; no authentic device values or live IRQ timings.','Original shared delay/ITCM/clock/timer-start/TON/status helper code executes; no successful return stubs.','Outputs compare ordered MMIO writes, actual child calls, selected globals and PRIMASK. Void callbacks do not claim meaningful R0 return.','M33-compatible ARMv8-M/FPU subset of stock M55.']),separators=(',',':'))+'\n');print('PASS',len(rows),'transition/timer comparisons')
