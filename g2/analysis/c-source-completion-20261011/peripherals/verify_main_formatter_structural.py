#!/usr/bin/env python3
"""Pinned Boot/Main IAR formatter instruction correspondence, no alias claim."""
from pathlib import Path
import hashlib,re,subprocess,json
R=Path(__file__).resolve().parents[4]
B=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
M=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
out=Path('/tmp/g2-main-format-structure');out.mkdir(exist_ok=True)
def read(image,base,address,size):return image[address-base:address-base+size]
def disassemble(name,raw,address):
 p=out/(name+'.bin');p.write_bytes(raw)
 text=subprocess.check_output(['arm-none-eabi-objdump','-D','-b','binary','-m','arm',
  '-M','force-thumb','--adjust-vma='+hex(address),str(p)],text=True)
 rows={}
 for line in text.splitlines():
  match=re.match(r'\s*([0-9a-f]+):\s+([0-9a-f ]+)\s+([a-z][a-z0-9.]*)\s*(.*)',line)
  if match:rows[int(match[1],16)-address]=(match[2].strip(),match[3],match[4].strip())
 return rows
def compare(name,boot_addr,main_addr,size):
 boot=read(B,0x410000,boot_addr,size);main=read(M,0x438000,main_addr,size)
 assert len(boot)==len(main)==size
 a=disassemble(name+'-boot',boot,boot_addr);b=disassemble(name+'-main',main,main_addr)
 assert a.keys()==b.keys()
 different=[]
 for offset in a:
  if a[offset][0]!=b[offset][0]:
   assert a[offset][1]==b[offset][1]=='bl',(name,offset,a[offset],b[offset])
   different.append({'offset':offset,'boot_target':a[offset][2],
                     'main_target':b[offset][2]})
 return {'name':name,'bytes':size,'instructions':len(a),'equal_bytes':sum(x==y for x,y in zip(boot,main)),
  'relocated_calls':different,'boot_sha256':hashlib.sha256(boot).hexdigest(),
  'main_sha256':hashlib.sha256(main).hexdigest()}
results=[compare('engine',0x41e47a,0x481836,3256),
         compare('integer',0x41f15c,0x482518,276),
         compare('emitter',0x41f2c8,0x482684,46),
         compare('double-primitives',0x422804,0x4d42f8,110)]
assert len(results[0]['relocated_calls'])==23
assert len(results[1]['relocated_calls'])==2
assert not results[2]['relocated_calls'] and results[2]['equal_bytes']==46
assert not results[3]['relocated_calls'] and results[3]['equal_bytes']==110
receipt=Path(__file__).with_name('main-formatter-structural.json')
receipt.write_text(json.dumps(results,indent=2)+'\n')
print('PASS_MAIN_FORMATTER_STRUCTURE',[(r['name'],r['instructions'],len(r['relocated_calls'])) for r in results])
