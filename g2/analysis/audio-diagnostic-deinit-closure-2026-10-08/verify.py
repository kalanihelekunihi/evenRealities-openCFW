from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];base=0x438000
record=0x75d404;src=record+struct.unpack_from('<I',raw,record-base)[0];encoded,dest=struct.unpack_from('<II',raw,record+4-base);p=src;end=p+(encoded>>1);data=bytearray()
while p!=end:
 assert p<end;t=raw[p-base];p+=1;l=t&3;m=t>>4
 if not l:l=raw[p-base]+3;p+=1
 if m==15:m=raw[p-base]+15;p+=1
 for i in range(l-1):data.append(raw[p-base]);p+=1
 if m:
  o=raw[p-base];p+=1;hi=(t>>2)&3
  if hi==3:hi=raw[p-base];p+=1
  o+=hi<<8;assert 0<o<=len(data)
  for i in range(m+2):data.append(data[-o])
assert dest==0x20080000 and len(data)==0xbbe6e
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(base,(len(raw)+4095)&~4095);u.mem_write(base,raw);u.mem_map(0x20000000,0x80000);u.mem_map(dest,0x200000);u.mem_write(dest,b'\xa5'*(len(data)+64));u.reg_write(UC_ARM_REG_R0,record);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x43a11f,0x2007f000,count=15000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert u.reg_read(UC_ARM_REG_R0)==record+12;assert bytes(u.mem_read(dest,len(data)))==data;assert bytes(u.mem_read(dest+len(data),64))==b'\xa5'*64
configs={hex(a):[hex(x) for x in struct.unpack_from('<7I',data,a-dest)] for a in [0x20106a7c,0x201074c0,0x20107f04]};(D/'startup-config-results.json').write_text(json.dumps(dict(status='PASS',compared_bytes=len(data),record=hex(record),source=hex(src),source_end=hex(end),compressed_bytes=encoded>>1,destination=hex(dest),decoded_sha256=hashlib.sha256(data).hexdigest(),configs=configs,limits=['Actual decoder versus independent Python, one whole authentic record. No full reset execution.']),indent=2)+'\n')
elf=Path('/tmp/opencfw-audio-deinit/deinit.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
Q=0x20006000;T=0x20005000;rows=[]
for mode,owner,callback,queue,file,initial_bits in itertools.product([0,1],[0x10b,0x999],[0,0x58f5e1],[0,1],[0,0x20008000],[0,0x800000]):
 vals=[]
 for entry in [0x58f74a if mode==0 else 0x58f806,sym['audio_diagnostic_deinit_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(base,(len(raw)+4095)&~4095);u.mem_write(base,raw);u.mem_map(0x20000000,0x80000);u.mem_map(dest,0x200000);u.mem_write(dest,bytes(data));u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
  w(0x20074a3c,1);w(0x20074a30,0);w(T+0x68,initial_bits);u.mem_write(T+0x6c,b'\x00');w(0x20003fa0,T);w(0x20003fa4,Q if queue else 0);w(0x20073c20+mode*12,owner,mode,callback);w(0x20073c08+mode*12,file,123,0x00ff4567);u.mem_write(0x20073c08+mode*12+10,b'\x01')
  if queue:
   u.reg_write(UC_ARM_REG_R0,50);u.reg_write(UC_ARM_REG_R1,12);u.reg_write(UC_ARM_REG_R2,Q+80);u.reg_write(UC_ARM_REG_R3,0);u.reg_write(UC_ARM_REG_SP,0x2007e000);w(0x2007e000,Q);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x441697,0x2007f000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
  boundary=[];calls=[]
  def code(u,a,n,d):
   if a in [0x57acd0,0x449238]:calls.append([hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)])
   if a==0x4745f4:boundary.extend([hex(a),u.reg_read(UC_ARM_REG_R0)]);u.emu_stop()
   if a==0x591374:boundary.extend([hex(a),*[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]]);u.emu_stop()
   assert a not in [0x43d574,0x43ce9e,0x4420bc,0x455370],'unexpected logger/yield/waiter'
  u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,mode);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=50000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  success=not callback or owner==0x10b;reg=bytes(u.mem_read(0x20073c20+12*mode,12));assert reg==(bytes(12) if callback and success else struct.pack('<III',owner,mode,callback))
  assert struct.unpack('<I',u.mem_read(T+0x68,4))[0]==initial_bits|(0x400000 if queue else 0)
  if queue:assert struct.unpack('<I',u.mem_read(Q+56,4))[0]==1;assert bytes(u.mem_read(Q+80,12))==struct.pack('<III',mode,1,0)
  if not success:assert not boundary and u.reg_read(UC_ARM_REG_R0)==0xffffffff
  vals.append((boundary,calls,None if boundary else u.reg_read(UC_ARM_REG_R0),reg,bytes(u.mem_read(0x20073c08,24)),bytes(u.mem_read(T,128)),bytes(u.mem_read(Q,800))))
 assert vals[0]==vals[1],(mode,owner,callback,queue,file,initial_bits,vals[0][:3],vals[1][:3]);rows.append(dict(mode=mode,owner=hex(owner),callback=hex(callback),queue=queue,file=hex(file),initial_flags=hex(initial_bits),boundary=vals[0][0],calls=vals[0][1]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['First-party deinit and independent recorder prefix, common actual queue/notify/unregister/encoder wrapper peers. No child result stubs.','File close and LC3 setup stop before first instruction; no stream free or encoder reinitialization completion.','Coherent initialized queue, nonwaiting synthetic TCB, taskcount0, optional preexisting exit flag. No live scheduling, DMA or callback concurrency.']),indent=2)+'\n');print('PASS',len(rows),'deinit comparisons;',len(data),'startup bytes',configs)
