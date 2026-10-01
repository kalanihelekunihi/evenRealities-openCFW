#!/usr/bin/env python3
"""Stock lag/angle instructions; host asin only is replaced mathematically."""
from pathlib import Path
import struct,json,hashlib,math
import unicorn,capstone
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';assert hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x59187a,0x59188e,0x5918b0,0x5918cc,0x591ba4,0x59c7ac,0x59c800];ranges=[(a,int(raw[a]['body_end_inclusive'],16)+1) for a in entries];records=[];lines=[]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB)
for a,z in ranges:
 data=B[a-BASE:z-BASE];h=hashlib.sha256(data).hexdigest();assert h==raw[a]['body_sha256'];records.append(dict(entry=hex(a),sha256=h));lines.append('\n%s SHA256 %s'%(hex(a),h));lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in md.disasm(data,a))
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB);u.mem_map(0x437000,0x35e000);u.mem_write(BASE,B);u.mem_map(0x20000000,0x400000);STOP=0x10000000;u.mem_map(STOP,4096);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
def dset(r,v):u.reg_write(r,struct.unpack('<Q',struct.pack('<d',v))[0])
def dget(r):return struct.unpack('<d',struct.pack('<Q',u.reg_read(r)))[0]
ASIN=[]
def hook(u,a,n,_):
 if a==0x43c260:
  x=dget(UC_ARM_REG_D0);ASIN.append(x);dset(UC_ARM_REG_D0,math.asin(x));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
 assert any(x<=a<z for x,z in ranges),hex(a)
u.hook_add(unicorn.UC_HOOK_CODE,hook)
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];L=f32(0x591cf4);RR=f32(0x591cf0);OUTPUT=0x20078000
CASES=[]
def run(a,args=(),stack=()):
 sp=0x203ff000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for r,v in zip(R,args):u.reg_write(r,v)
 for i,v in enumerate(stack):u.mem_write(sp+4*i,struct.pack('<I',v))
 u.emu_start(a|1,STOP,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==STOP
 return u.reg_read(R[0])
def buffers(l,r):
 u.mem_write(L,struct.pack('<%dh'%len(l),*l));u.mem_write(RR,struct.pack('<%dh'%len(r),*r))
def analyze(l,r,limit=10,energy=0.,quality=0.):
 buffers(l,r)
 for i,v in enumerate([16000.,.14,343.,energy,quality]):dset(UC_ARM_REG_D0+i,v)
 run(0x5918cc,[L,RR,len(l),limit],[OUTPUT+8*i for i in range(4)])
 return struct.unpack('<4d',u.mem_read(OUTPUT,32))
def clean(v):return 'NaN' if math.isnan(v) else v
for lag in [-10,-3,-1,0,1,3,10]:
 l=[0]*800;r=[0]*800;l[400]=1000;r[400+lag]=1000
 angle,delay,q,rms=analyze(l,r);expected=math.asin(max(-1.,min(1.,lag/16000*343/.14)))
 assert math.isclose(angle,expected,abs_tol=1e-12) and math.isclose(delay,lag/16000,abs_tol=1e-12)
 ret=run(0x591ba4);signed=ret if ret<0x80000000 else ret-0x100000000;assert signed==int(math.degrees(expected))
 CASES.append(dict(case='impulse_lag_%d'%lag,angle=angle,delay=delay,quality=q,rms=rms,wire_degrees=signed))
for name,l,r,lim,en,qual in [('silence',[0]*800,[0]*800,10,0,0),('default_lag_limit',[0]*800,[0]*800,0,0,0),('energy_reject',[1]*800,[1]*800,10,2,0),('quality_reject',[1]*800,[1]*800,10,0,2),('empty',[],[],10,0,0)]:
 if not l:
  for i,v in enumerate([16000.,.14,343.,en,qual]):dset(UC_ARM_REG_D0+i,v)
  run(0x5918cc,[L,RR,0,lim],[OUTPUT+8*i for i in range(4)]);vals=struct.unpack('<4d',u.mem_read(OUTPUT,32))
 else:vals=analyze(l,r,lim,en,qual)
 if name in ('silence','default_lag_limit'):assert math.isclose(vals[0],-math.pi/2) and vals[2]==0 and vals[3]==0
 else:assert math.isnan(vals[0]) and math.isnan(vals[1])
 CASES.append(dict(case=name,outputs=list(map(clean,vals))))
buffers([0]*800,[0]*800);ret=run(0x591ba4);assert ret==0xffffffa6;CASES.append(dict(case='stock_wrapper_silence',wire_degrees=-90))
(OUT/'validation.json').write_text(json.dumps(dict(image_sha256=SHA,functions=records,left_buffer=hex(L),right_buffer=hex(RR),cases=CASES,asin_arguments=ASIN,limits='Original Thumb/VFP correlation, integer-to-double, nonnegative sqrt, clamp and degree conversion. Only asin is a host math stub. Unicorn Thumb without MCLASS is used because its MCLASS model rejects double VFP. Synthetic PCM, no acoustic/hardware validation.'),indent=2)+'\n')
print('PASS',len(CASES),'cases;',len(records),'body hashes')
