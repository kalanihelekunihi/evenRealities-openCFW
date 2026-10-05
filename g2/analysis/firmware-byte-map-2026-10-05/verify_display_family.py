#!/usr/bin/env python3
"""Bounded binary-decoder variable-source path; external state providers are stubs."""
from pathlib import Path
import hashlib,json,struct,csv,re
import unicorn,capstone
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'display-proof';OUT.mkdir(exist_ok=True);B=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();BASE=0x437fe0;SHA='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';assert hashlib.sha256(B).hexdigest()==SHA
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB);md.detail=True
syms={int(r['address'],16):r for r in csv.DictReader((ROOT/'g2/symbols/apollo_main.tsv').open(),delimiter='\t')};records=[]
def body(a,z=None):
 if z is None:
  r=syms[a];z=int(r['end'],16);assert hashlib.sha256(B[a-BASE:z-BASE]).hexdigest()==r['stock_sha256']
 raw=B[a-BASE:z-BASE];records.append(dict(start=a,end_exclusive=z,sha256=hashlib.sha256(raw).hexdigest(),catalogue_bound=a in syms and z==int(syms[a]['end'],16)));return list(md.disasm(raw,a))
ins=body(0x5bf332);helper=body(0x5bf2f8);assert any(i.mnemonic=='bl' and i.op_str=='#0x498680' for i in helper)
assets={a['descriptor_runtime']:a for a in json.loads((OUT.parent/'display-image-candidates.json').read_text())};family=[]
for n,i in enumerate(ins):
 if i.mnemonic=='bl' and i.op_str=='#0x5bf2f8' and n>=2:
  load=ins[n-2];mov=ins[n-1]
  if load.mnemonic not in ['ldr','ldr.w'] or not load.op_str.startswith('r1, [pc, #') or mov.op_str!='r0, r5':continue
  imm=int(re.search(r'#(0x[0-9a-f]+)',load.op_str)[1],16);literal=((load.address+4)&~3)+imm;ptr=struct.unpack_from('<I',B,literal-BASE)[0]
  if ptr in assets and len(family)<6:family.append(dict(asset=assets[ptr],load_pc=load.address,call_pc=i.address,literal_runtime=literal,literal_bytes=B[literal-BASE:literal-BASE+4].hex()))
assert len(family)==6
original_ranges=[(0x4c794c,0x4c79ce),(0x4c79d0,0x4c7b1c),(0x4c7b24,0x4c7e22),(0x454738,0x454746),(0x439be4,0x439c8a),(0x48b762,0x48b7a6),(0x48aef8,0x48affa),(0x48aa54,0x48aa60)]
for a,z in original_ranges:body(a,z)
# Callback boundaries are proved by registration pointers/return instructions, not complete historical catalogue coverage.
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB);u.mem_map(0x437000,0x35e000);u.mem_write(BASE,B);u.mem_map(0x20000000,0x400000);STOP=0x10000000;u.mem_map(STOP,4096);REG=0x20070000;CTX=0x20071000;WORK=0x20072000;RAMDSC=0x20073000;trace={};reads=[];current=-1;cases=[];stubs=[]
def put(a,v):u.mem_write(a,struct.pack('<I',v))
def val(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def ret(v=None):
 if v is not None:u.reg_write(UC_ARM_REG_R0,v)
 u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
def hook(u,a,n,_):
 if a==0x4890c8:stubs.append(a);ret(REG);return
 if a==0x454746:
  stubs.append(a);r0=u.reg_read(UC_ARM_REG_R0);u.mem_write(r0,bytes([u.reg_read(UC_ARM_REG_R1)&255])*u.reg_read(UC_ARM_REG_R2));ret();return
 if a==0x4c81a2:stubs.append(a);put(CTX+0x48,WORK);ret(WORK);return
 if a==0x48ab04:stubs.append(a);ret();return # alignment provider returns existing pixel pointer, L8 path only
 if a==0x489168:stubs.append(a);ret(u.reg_read(UC_ARM_REG_R1));return # cache/postprocess provider leaves buffer unchanged
 if a==0x44d25c:stubs.append(a);ret();return
 assert any(x<=a<a+n<=z for x,z in original_ranges),hex(a)
 raw=bytes(u.mem_read(a,n));off=a-BASE;assert B[off:off+n]==raw
 row=trace.setdefault(a,dict(runtime_pc=a,payload_range=[off,off+n],instruction_bytes=raw.hex(),sha256=hashlib.sha256(raw).hexdigest(),case_indices=[]));assert row['instruction_bytes']==raw.hex()
 if current not in row['case_indices']:row['case_indices'].append(current)
def read(u,access,a,n,value,_):
 if BASE<=a<a+n<=BASE+len(B):reads.append(dict(case_index=current,runtime=a,payload_range=[a-BASE,a-BASE+n]))
u.hook_add(unicorn.UC_HOOK_CODE,hook);u.hook_add(unicorn.UC_HOOK_MEM_READ,read)
def run(a,args):
 u.reg_write(UC_ARM_REG_SP,0x203ff000);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.emu_start(a|1,STOP,count=10000);assert u.reg_read(UC_ARM_REG_PC)==STOP;return u.reg_read(UC_ARM_REG_R0)
current=0;run(0x4c794c,[]);assert [val(REG+i*4) for i in range(4)]==[0x4c79d1,0x4c7b25,0x4c7e4d,0x4c7e29];cases.append({'case':'registration','callbacks':[val(REG+i*4) for i in range(4)]})
for f in family:
 a=f['asset'];current=len(cases);u.mem_write(CTX,b'\0'*0x80);u.mem_write(WORK,b'\0'*0x80);put(CTX+0xc,a['descriptor_runtime']);assert run(0x4c79d0,[REG,CTX,CTX+0x20])==1;assert bytes(u.mem_read(CTX+0x20,12))==B[a['descriptor_payload_offset']:a['descriptor_payload_offset']+12]
 assert run(0x4c7b24,[REG,CTX])==1;out=val(CTX+0x2c);assert out==WORK+0x24;raw=bytes(u.mem_read(out,28));header=struct.unpack('<7I',raw);d=struct.unpack_from('<7I',B,a['descriptor_payload_offset']);assert header[:5]==d[:5] and header[5]==d[4];cases.append(dict(case='variable_L8',descriptor=a['descriptor_runtime'],output_buffer=out,output_header_and_storage_words=list(header),pixel_range=a['data_runtime_range']))
# Rejection path proves the constructor checks storage capacity; test RAM copy is not a map claim.
current=len(cases);a=family[0]['asset'];raw=bytearray(B[a['descriptor_payload_offset']:a['descriptor_payload_offset']+28]);struct.pack_into('<I',raw,12,a['width']*a['height']-1);u.mem_write(RAMDSC,bytes(raw));assert run(0x48b762,[WORK,RAMDSC])==0;cases.append({'case':'storage_size_short_rejected'})
rows=sorted(trace.values(),key=lambda r:r['runtime_pc'])
for r in rows:
 ins=list(md.disasm(bytes.fromhex(r['instruction_bytes']),r['runtime_pc']));assert len(ins)==1 and ins[0].size==len(bytes.fromhex(r['instruction_bytes']));r.update(mnemonic=ins[0].mnemonic,operands=ins[0].op_str)
assert all(x['payload_range'][1]<=y['payload_range'][0] for x,y in zip(rows,rows[1:]));(OUT/'executed-instructions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(OUT/'immutable-data-reads.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in reads))
report=dict(firmware_sha256=SHA,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_body_hashes=records,case_count=len(cases),cases=cases,family=family,unique_original_instruction_bytes=sum(len(bytes.fromhex(r['instruction_bytes'])) for r in rows),stub_addresses=sorted(set(stubs)),limits='Original registration/header/open/copy/draw-buffer validation instructions. Synthetic decoder context; registry allocator, zero helper, workspace allocator, alignment adapter, cache/postprocess and logging are stubs. No renderer pixel reads or live UI trace; copied geometry/storage proves typed buffer admission, not visual fidelity or complete decoder behavior. Literal loads/direct BL prove family constructor source arguments statically; constructor itself not executed.')
report['executed_trace_sha256']=hashlib.sha256((OUT/'executed-instructions.jsonl').read_bytes()).hexdigest()
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(cases),'cases;',len(family),'attributed descriptors;',report['unique_original_instruction_bytes'],'instruction bytes')
