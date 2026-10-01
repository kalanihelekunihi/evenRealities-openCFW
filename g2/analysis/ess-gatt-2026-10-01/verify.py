#!/usr/bin/env python3
"""Bounded original Thumb execution; external transport/scheduler providers stubbed."""
from pathlib import Path
import struct,json,hashlib,uuid
import unicorn,capstone
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0
SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';assert hashlib.sha256(B).hexdigest()==SHA
raw={int(r['entry'],16):r for r in map(json.loads,(ROOT/'g2/research/corpus/apollo-main/ghidra/open-2026-09-29/functions-000.jsonl').read_text().splitlines())}
entries=[0x4b503c,0x4b5204,0x56c6fc];ranges=[(a,int(raw[a]['body_end_inclusive'],16)+1) for a in entries]+[(0x5361ec,0x5361f6),(0x5361f6,0x5361fe)]
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);records=[];lines=[]
for a,z in ranges:
 data=B[a-BASE:z-BASE];h=hashlib.sha256(data).hexdigest()
 if a in raw:assert h==raw[a]['body_sha256']
 records.append(dict(entry=hex(a),end_exclusive=hex(z),sha256=h));lines.append('\n%s..%s SHA256 %s'%(hex(a),hex(z),h));lines.extend('%08x %-10s %-8s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str) for i in md.disasm(data,a))
(OUT/'disassembly.txt').write_text('\n'.join(lines)+'\n')
def f32(a):return struct.unpack_from('<I',B,a-BASE)[0]
R=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];STOP=0x10000000;CORE=0x20078000;SERVER=CORE+0x100;MSG=CORE+0x200;PACKET=CORE+0x300
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS);u.mem_map(0x437000,0x35e000);u.mem_write(BASE,B);u.mem_map(0x20000000,0x400000);u.mem_map(STOP,4096)
def w32(a,v):u.mem_write(a,struct.pack('<I',v))
def h16(a):return struct.unpack('<H',u.mem_read(a,2))[0]
def run(a,*args):
 u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for r,v in zip(R,args):u.reg_write(r,v)
 u.emu_start(a|1,STOP,count=10000000);assert u.reg_read(UC_ARM_REG_PC)==STOP
 return u.reg_read(R[0])
u.reg_write(UC_ARM_REG_R9,0);run(0x43a11e,0x75d3f4)
ramhash=hashlib.sha256(u.mem_read(0x20000000,17752)).hexdigest();assert ramhash=='df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743'
CALLS=[];CASES=[];acl=251;features=0
STUB={0x5353ae:'add_group',0x4b5074:'callback',0x4b4eee:'core_by_conn',0x52d7c4:'features',0x4c9c50:'logging_off',0x43d0ce:'logging_off',0x43ce9e:'log',0x43d574:'log',0x52a63c:'log',0x530d4c:'acl_rx_max',0x4b50ae:'allocate',0x4b50ba:'l2cap',0x534c9a:'error'}
def hook(u,a,n,_):
 if a not in STUB:
  assert any(x<=a<z for x,z in ranges),hex(a);return
 name=STUB[a];v=[u.reg_read(r) for r in R];ret=0
 if name=='core_by_conn':ret=CORE
 if name=='features':u.mem_write(v[1],bytes([features]))
 if name=='acl_rx_max':ret=acl
 if name=='allocate':ret=PACKET
 if name not in ('logging_off','log'):CALLS.append(dict(call=name,args=v))
 u.reg_write(R[0],ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
u.hook_add(unicorn.UC_HOOK_CODE,hook)
def save(name,**kw):CASES.append(dict(case=name,calls=list(CALLS),**kw));CALLS.clear()
g=f32(0x536200);assert g==0x20003b38
run(0x5361f6,0,0x4be2b5);assert struct.unpack('<II',u.mem_read(g+8,8))==(0,0x4be2b5)
run(0x5361ec);assert CALLS[-1]['args'][0]==g;save('ESS_callbacks_and_group_registration',group=hex(g))
nextp,table,rd,wr,start,end=struct.unpack('<IIIIHH',u.mem_read(g,20));assert (table,start,end)==(0x6de9d4,0x860,0x865)
attrs=[]
for i in range(end-start+1):
 up,vp,lp,mx,settings,perm=struct.unpack('<IIIHBB',u.mem_read(table+16*i,16));n=h16(lp)
 uid=bytes(u.mem_read(up,16 if settings&1 else 2));val=bytes(u.mem_read(vp,n)) if vp<0x20000000 else None
 attrs.append(dict(handle=hex(start+i),uuid_bytes=uid.hex(),value_hex=val.hex() if val is not None else None,length=n,max_length=mx,settings=hex(settings),permissions=hex(perm)))
assert attrs[0]['value_hex']=='50642ec78a0e7390e111c20860270000'
assert attrs[1]['value_hex']=='04620801642ec78a0e7390e111c20860270000'
assert attrs[3]['value_hex']=='10640802642ec78a0e7390e111c20860270000'
assert attrs[4]['uuid_bytes']=='02642ec78a0e7390e111c20860270000'
ccc=f32(0x4b8744);cccrows=[struct.unpack('<HHH',u.mem_read(ccc+6*i,6)) for i in range(6)];assert cccrows[3]==(0x865,1,0)
save('decoded_GATT_tables',attributes=attrs,ccc_table=[list(x) for x in cccrows])
for peer,local,bearer in [(23,247,0),(208,247,0),(517,247,0),(247,208,1)]:
 u.mem_write(CORE,b'\x00'*20);u.mem_write(CORE+14,b'\x09');run(0x4b503c,CORE,bearer,peer,local);assert h16(CORE+4*bearer)==min(peer,local)
 assert CALLS[-1]['args'][:3]==[9,22,0];save('setter_%d_%d_bearer%d'%(peer,local,bearer),stored=h16(CORE+4*bearer))
u.mem_write(CORE,struct.pack('<H',208));assert run(0x4b5204,9)==208;save('AttGetMtu_returns_unadjusted_u16')
for peer in [23,207,208,247,517]:
 u.mem_write(CORE,b'\x00'*20);w32(SERVER+16,CORE);u.mem_write(SERVER+36,b'\x09\x00');u.mem_write(MSG+9,struct.pack('<H',peer));run(0x56c6fc,SERVER,0,MSG,0)
 assert h16(CORE)==247;assert bytes(u.mem_read(PACKET+8,3))==b'\x03\xf7\x00';save('incoming_MTU_%d'%peer,stored=h16(CORE),response=bytes(u.mem_read(PACKET+8,3)).hex())
features=2;u.mem_write(CORE,struct.pack('<H',23));run(0x56c6fc,SERVER,0,MSG,0);assert h16(CORE)==23 and any(c['call']=='error' for c in CALLS);save('feature_bit_reject_leaves_MTU')
evidence=[]
for a,z in [(0x4b7ec2,int(raw[0x4b7ec2]['body_end_inclusive'],16)+1),(0x6de9d4,0x6dea34),(0x7894d0,0x789500),(0x783adc,0x783b03),(0x7518c0,0x7518e4)]:
 evidence.append(dict(start=hex(a),end_exclusive=hex(z),sha256=hashlib.sha256(B[a-BASE:z-BASE]).hexdigest()))
(OUT/'validation.json').write_text(json.dumps(dict(image_sha256=SHA,load_base=hex(BASE),initializer_sha256=ramhash,functions=records,static_evidence=evidence,cases=CASES,limits='Original instructions with synthetic connection state; logging, feature provider, allocator, callback, GATT insertion and L2CAP transport are stubs. No live GATT discovery, peer negotiation, scheduler or radio trace.'),indent=2)+'\n')
print('PASS',len(CASES),'cases;',len(records),'code hashes')
