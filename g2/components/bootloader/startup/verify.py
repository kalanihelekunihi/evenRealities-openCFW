#!/usr/bin/env python3
"""Original/source startup helpers, real records plus synthetic valid streams.
Compressed official bytes are test inputs, not source-defined rebuilt payload.
"""
import argparse,importlib.util,json,struct,hashlib,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('bootv',ROOT/'g2/components/bootloader/update_core/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
v.ENTRIES.update(expand_record=0x415326,zero_table=0x431e38)
OUT=0x20030000;REC=0x20032000;INPUT=0x20033000
class Machine(v.Machine):
 def __init__(self,*args,**kw):
  super().__init__(*args,**kw);self.cpu.mem_map(0,0x10000);self.cpu.mem_map(0x20040000,0xc0000)
  self.cpu.mem_write(OUT,b'\xcc'*4096);self.cpu.mem_write(0,b'\xcc'*256)
 def code(self,uc,pc,size,user):
  if not self.source and hasattr(self,'stream_bounds'):
   start,end,dest=self.stream_bounds;zero=bool(uc.reg_read(v.a.UC_ARM_REG_CPSR)&(1<<30))
   if pc in [0x415340,0x415356,0x41535e,0x41536e] or (zero and pc in [0x41534a,0x41537a]):
    address=uc.reg_read(v.a.UC_ARM_REG_R3);assert start<=address<end,('original compressed read',hex(pc),hex(address));self.stream_reads.add(address)
   if pc==0x41538e and not zero:
    back=uc.reg_read(v.a.UC_ARM_REG_R0);output=uc.reg_read(v.a.UC_ARM_REG_R5);assert dest<=back<output,('original backreference',hex(back),hex(output))
  super().code(uc,pc,size,user)
 def invoke(self,name,record,base=0):
  self.cpu.reg_write(v.a.UC_ARM_REG_R9,base);d=self.run(name,[record,base]);d['output_sha']=hashlib.sha256(self.cpu.mem_read(OUT,4096)).hexdigest();d['itcm_sha']=hashlib.sha256(self.cpu.mem_read(0,256)).hexdigest();return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--elf',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();assert v.sha(v.BLOB)==v.SHA;_,seg,sym=v.elf.elf_info(args.elf);blob=v.BLOB.read_bytes();trace={};cases=[]
 def pair():return [Machine(),Machine(True,seg,sym)]
 def check(name,ms,record,base=0,meta=None,region=None):
  try:d=[m.invoke(name,record,base) for m in ms]
  except Exception:
   print('fixture failed',name,meta,[(m.source,hex(m.cpu.reg_read(v.a.UC_ARM_REG_PC))) for m in ms]);raise
  assert d[0]==d[1],(name,meta,{k:[x[k] for x in d] for k in d[0] if d[0][k]!=d[1][k]});trace.update(ms[0].trace)
  if region:
   a,n=region;raw=[bytes(m.cpu.mem_read(a,n)) for m in ms];assert raw[0]==raw[1];d[0]['region_sha256']=hashlib.sha256(raw[0]).hexdigest()
  cases.append({'function':name,'record':hex(record),'base':base,'fixture':meta,'result':d[0]})
 rng=random.Random(61006)
 # Literal count is token low bits minus one; extended count is nextbyte+2.
 streams=[b'\x01',b'\x02A',b'\x03AB',b'\x00\x03ABCDE',b'\x12A\x01',b'\xf2\x00Z\x01',b'\x13AB\x02']
 for stream in streams:
  for relative in [False,True]:
   ms=pair();base=0x20000000 if relative else 0;dst=OUT-base
   for m in ms:m.cpu.mem_write(INPUT,stream);m.cpu.mem_write(REC,struct.pack('<III',INPUT-REC,len(stream)*2+int(relative),dst))
   check('expand_record',ms,REC,base,{'stream':stream.hex(),'relative':relative})
 # Complete official input ranges: no guessed RAM prefix or post-EOF bytes.
 for rec,src,n,dest,size in [(0x4330f4,0x434461,22,0x40,24),(0x433104,0x4341c0,625,0x20000000,1371),(0x433114,0x434431,48,0x20080000,4096)]:
  ms=pair()
  for m in ms:
   m.cpu.mem_write(rec,blob[rec-v.BASE:rec-v.BASE+12]);m.cpu.mem_write(src,blob[src-v.BASE:src-v.BASE+n]);m.stream_reads=set()
   m.stream_bounds=(src,src+n,dest)
  check('expand_record',ms,rec,meta={'official':True,'source':[hex(src),hex(src+n)],'output':[hex(dest),size]},region=(dest,size))
  assert ms[0].stream_reads==set(range(src,src+n)),('complete original stream consumption',hex(src))
  assert ms[0].cpu.reg_read(v.a.UC_ARM_REG_R3)==src+n
 # Word/halfword/byte tails; raw stock precondition size>=4 per nonzero row.
 for size in [4,5,6,7,8,15,16,31,32,4096]:
  for relative in [False,True]:
   ms=pair();base=0x20000000 if relative else 0;dst=OUT-base+int(relative)
   for m in ms:m.cpu.mem_write(REC,struct.pack('<III',size,dst,0))
   check('zero_table',ms,REC,base,{'size':size,'relative':relative})
 ms=pair()
 for m in ms:m.cpu.mem_write(REC,b'\0'*4)
 check('zero_table',ms,REC,meta={'empty':True})
 # Exact image table clears two ranges; stack is outside both clear ranges.
 ms=pair()
 for m in ms:
  m.cpu.mem_write(0x4330dc,blob[0x230dc:0x230f0]);m.cpu.mem_write(0x2000055c,b'\xcc'*0x26c6c);m.cpu.mem_write(0x20081000,b'\xcc'*0x74100)
 check('zero_table',ms,0x4330dc,meta={'official':True},region=(0x20081000,0x74100))
 assert all(bytes(m.cpu.mem_read(a,n))==b'\0'*n for m in ms for a,n in [(0x2000055c,0x26c6c),(0x20081000,0x74100)])
 used={int(pc,0)+i for pc,raw in trace.items() for i in range(len(bytes.fromhex(raw)))}
 d={'status':'PASS','cases':len(cases),'comparisons':cases,'original_trace':trace,'distinct_original_trace_bytes':len(used),'original_sha256':v.SHA,'elf_sha256':v.sha(args.elf),'source_sha256':{p.name:v.sha(p) for p in Path(__file__).parent.iterdir() if p.suffix in ['.c','.h','.py','.ld']},'limits':['No original returning provider stubs; actual original startup helper instructions execute.','Official compressed streams are authenticated test data, not a source-defined full firmware image or source-defined ITCM implementation.','Full reset/FPU/stack-limit/SBL/RAM-vector producer/RTOS entry remain outside these helper tests.','Raw APIs lack bounds checks; malicious/truncated input or size1..3 zero rows are not tested-safe.','Compatible Cortex-M4 source profile is separated from actual Cortex-M55 build.']};args.output.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'status':'PASS','cases':len(cases),'original_bytes':len(used),'official_stream_outputs':[c['fixture'] for c in cases if c['fixture'].get('official')]},indent=2))
if __name__=='__main__':main()
