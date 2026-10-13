#!/usr/bin/env python3
"""Full linked CASE router RAM-only families: actual native/C, no stubs."""
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
import hashlib,json,random,struct
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;elf=H/'qualified/case.elf';fw=R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rng=random.Random(0x1e94)
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
assert sha(fw)=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';cases=[];rows=[]
lengths=[2,4,6,8,10,12,16,32,37,64,128,255]
for side in [0,1]:
 for position in range(4):
  for command in [0,7,8,0x13,0x3e,0x46,0x58,0x59,0x5a,0x5b]:
   for i in range(32):
    ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=1;packet=bytearray(rng.randbytes(0x118));length=lengths[i%len(lengths)];start=position+4;packet[position:position+4]=bytes([0x5a,0xa5,0xff,length]);packet[start]=command
    if command==0x13:packet[start+3]=[0,1,6,255][i%4];packet[start+7]=[0,97,98,99,100,255][i%6];packet[start+8]=[0,1,255][i%3];packet[start+9]=[0,1,127,255][i%4]
    elif command==0x58:packet[start+3]=[0,1,0x20,255][i%4];packet[start+9]=[0,1,2,255][i%4];packet[start+10]=[0,0x39,0x3a,255][(i//4)%4]
    elif command in [0x59,0x5b]:packet[start+3]=[0,1,2,255][i%4];packet[start+4]=[0,1,4,255][(i//4)%4]
    elif command==0x3e:packet[start+4]=[0,1,4,255][i%4]
    elif command==0x5a:
     n=i*8+1;packet[start+3]=n;packet[start+n+3]=(sum(packet[start+4:start+n+3])+(i%2))&255
    packet[start+length]=(length-2+sum(packet[start:start+length]))&255;ram[0x664:0x77c]=packet
    # Explicit counter threshold and prior flag/history combinations.
    struct.pack_into('<I',ram,0x89c+(17 if side==0 else 10)*4,[0,9,10,11,0xffffffff][i%5]);ram[0xf4]=i&1;ram[0xf5]=(i>>1)&1;ram[0xb4]=[0,1,127,255][i%4];ram[0xb5]=[0,1,127,255][(i//4)%4]
    cases.append({'side':side,'position':position,'command':command,'length':length,'index':i,'ram':bytes(ram)})
# No header and bad outer CRC5A never invoke diagnostic/forwarding children.
for i in range(64):
 ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=1;ram[0x664:0x77c]=bytes(0x118);cases.append({'side':i&1,'position':None,'command':None,'index':i,'ram':bytes(ram)})
for side in [0,1]:
 for position in range(4):
  for length in [0,1,2,3,6,9,16,64,128,255]:
   ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=1;p=bytearray(rng.randbytes(0x118));s=position+4;p[position:s]=bytes([0x5a,0xa5,0xff,length]);p[s]=0x5a
   if length>0:p[s+length]=(length-2+sum(p[s:s+length])+1)&255
   ram[0x664:0x77c]=p;cases.append({'side':side,'position':position,'command':0x5a,'length':length,'bad_CRC':True,'ram':bytes(ram)})
# Every opcode's bad-CRC branch is hardware-free when the real hex logger
# observes the same quiet flag. Include length-zero aliasing deliberately.
for command in range(256):
 for length in [0,1,2,255]:
  for side in [0,1]:
   if length==0 and command==0xfe:continue
   position=(command+side)%4;ram=bytearray(rng.randbytes(0x3000));ram[0xbf]=1;p=bytearray(rng.randbytes(0x118));start=position+4;p[position:start]=bytes([0x5a,0xa5,0xff,length]);p[start]=command
   if length>0:p[start+length]=(length-2+sum(p[start:start+length])+1)&255
   ram[0x664:0x77c]=p;cases.append({'side':side,'position':position,'command':command,'length':length,'bad_CRC':True,'all_opcode_error_domain':True,'ram':bytes(ram)})
for index,c in enumerate(cases):
 pair=[]
 for native in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,0x20000)
  if native:u.mem_write(0x08000000,fw.read_bytes()[32:])
  else:
   for a,b in seg:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,c['ram']);u.reg_write(UC_ARM_REG_R0,c['side']);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x2000f001)
  u.emu_start((0x08001e94 if native else sym['case_record_dispatch_1e94'])|1,0x2000f000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x2000f000,('did_not_return',index,native,c['command'],hex(u.reg_read(UC_ARM_REG_PC)))
  assert u.reg_read(UC_ARM_REG_SP)==0x20008000;pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000000,0x3000))))
 if pair[0]!=pair[1]:
  diff=[{'offset':hex(i),'native':a,'source':b,'initial':c['ram'][i]} for i,(a,b) in enumerate(zip(pair[0][1],pair[1][1])) if a!=b];r={'status':'FAIL_NATIVE_C_ROUTER','case_index':index,'case':{k:v for k,v in c.items() if k!='ram'},'native_return':pair[0][0],'source_return':pair[1][0],'RAM_differences':diff,'ELF_sha256':sha(elf)};(H/'failure.json').write_text(json.dumps(r,indent=2)+'\n');(H/'failure-input.bin').write_bytes(c['ram']);raise AssertionError(r)
 rows.append({k:v for k,v in c.items() if k!='ram'})
r={'status':'PASS_FULL_LINKED_ROUTER_RAM_FAMILIES','cases':len(rows),'ELF_sha256':sha(elf),'firmware_sha256':sha(fw),'comparisons':rows,'limits':['Full actual source graph and native bodies; no child stubs/cuts or hardware models. Loggingdisabled; tenRAM-only commandfamilies plusnoheader andall256opcode badCRC paths through genuine quiethexlogger.','Forwarding/default commands and diagnostic logging/hardware effects remain separate; no wholeCASE/nativebytecoverage promotion.']};(H/'verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['cases'])
