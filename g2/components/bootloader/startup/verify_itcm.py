#!/usr/bin/env python3
"""Initialize original ITCM by stock instructions, compare source assembly."""
import argparse,importlib.util,json,random,hashlib
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.ENTRIES.update(expand_record=0x415326,itcm_countdown=0x40,itcm_noop_46=0x46,itcm_word_copy=0x48,itcm_noop_56=0x56)
INPUT=0x20032000;OUTPUT=0x20033000
class Machine(v.Machine):
 def __init__(self,source=False,text=b'',symbols=None):
  super().__init__(source,[],symbols);self.cpu.mem_map(0,0x10000)
  if source:self.cpu.mem_write(0x40,text);self.exec_ranges=[(0x40,0x58)]
  else:self.run('expand_record',[0x4330f4,0]);self.exec_ranges.append((0x40,0x58));self.trace={}
 def invoke(self,name,args):
  d=self.run(name,args);d['copied_sha256']=hashlib.sha256(self.cpu.mem_read(OUTPUT,256)).hexdigest();d['registers']=[self.cpu.reg_read(r) for r in [v.a.UC_ARM_REG_R0,v.a.UC_ARM_REG_R1,v.a.UC_ARM_REG_R2,v.a.UC_ARM_REG_R3]];return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 with a.elf.open('rb') as f:
  e=ELFFile(f);assert e.elfclass==32 and e.little_endian and e['e_machine']=='EM_ARM';text=e.get_section_by_name('.text');assert text['sh_addr']==0x40 and text['sh_size']==24;data=text.data();symbols={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols() if x.name and x['st_shndx']!='SHN_UNDEF'}
 ms=[Machine(),Machine(True,data,symbols)];original=bytes(ms[0].cpu.mem_read(0x40,24));assert data==original
 cases=[];trace={};rng=random.Random(61006)
 def check(name,args):
  d=[m.invoke(name,args) for m in ms];assert d[0]==d[1],(name,args,d);trace.update(ms[0].trace);cases.append({'function':name,'arguments':args,'result':d[0]})
 for n in [1,2,3,7,16,31,255]:check('itcm_countdown',[n,0x1234,0x5678,0xabcd])
 for name in ['itcm_noop_46','itcm_noop_56']:check(name,[0x1234,0x5678,0xabcd,0x9876])
 for n in [1,2,3,7,16,31,64]:
  payload=rng.randbytes(n*4)
  for m in ms:m.cpu.mem_write(INPUT,payload);m.cpu.mem_write(OUTPUT,b'\xcc'*256)
  check('itcm_word_copy',[INPUT,OUTPUT,n,0xabcdef])
  assert all(bytes(m.cpu.mem_read(OUTPUT,n*4))==payload for m in ms)
 d={'status':'PASS','cases':len(cases),'comparisons':cases,'original_sha256':v.SHA,'elf_sha256':v.sha(a.elf),'decoded_itcm_sha256':hashlib.sha256(original).hexdigest(),'source_text_equals_original_decoded_24_bytes':True,'original_trace':trace,'source_sha256':{p.name:v.sha(p) for p in [Path(__file__),Path(__file__).with_name('itcm_helpers.S'),Path(__file__).with_name('itcm.ld')]},'limits':['Original ITCM is produced by executing stock initializer on the authenticated22byte compressed stream; no executable donor data is embedded in source.','Source assembly text matches all24 decoded bytes; this does not prove the original22byte IAR compressed representation is source-generated or matched.','Counts are instruction-loop/word counts, not calibrated delay time. Zero counts underflow and are outside valid bounded fixtures.','No timing/cache/silicon or complete firmware byte identity proof.','Decoded ITCM instructions have runtime addresses outside raw payload; do not add24 expanded bytes to stored-payload coverage.']};a.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'decoded_bytes_equal':len(data)},indent=2))
if __name__=='__main__':main()
