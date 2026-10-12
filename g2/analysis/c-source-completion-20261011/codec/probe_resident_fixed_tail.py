#!/usr/bin/env python3
"""Place source resident body before exact stock vector and initialized tail."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
TOOL=ROOT/'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
RD=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
KNOWN=Path(__file__).with_name('image_a_known_data.ld')
START=0x10023400;BODY_START=0x10023500;TAIL_START=0x100264e4;END=0x10026d7c

def resident(n):
 if n=='.text':return True
 if n.startswith(('.text.gx8002_resident_','.rodata.gx8002_resident_')) and '10203c74' not in n:return True
 if n.startswith('.gx8002.') and not n.startswith(('.gx8002.sample_name.','.gx8002.flash_name.','.gx8002.xip.')):return True
 return False

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 source=json.loads(a.closure.read_text());sha=hashlib.sha256(a.candidate.read_bytes()).hexdigest();assert source['candidate_sha256']==sha
 sections={r['section']:r for r in source['all_alloc_progbits']['sections'] if resident(r['section'])}
 rows=[]
 for l in KNOWN.read_text().splitlines():
  m=re.search(r'^\s*(\.\S+)\s+(0x[0-9a-f]+)\s*:\s*\{\s*KEEP\(\*\((\.\S+)\)\)',l)
  if m and m[3] in sections:rows.append((m[1],int(m[2],16),m[3]))
 assert rows[0][1]==START and rows[-1][1]<END
 fixed={r[2] for r in rows};body=[s for n,s in sections.items() if n not in fixed]
 body.sort(key=lambda item: item['section']!='.text.gx8002_resident_reset_entry_23500')
 assert body[0]['section']=='.text.gx8002_resident_reset_entry_23500'
 assert [r[1] for r in rows[1:4]]==[0x10025cd0,0x10025ce0,0x10025cf4]
 internal_start=rows[1][1]
 internal_end=rows[3][1]+sections[rows[3][2]]['bytes']
 assert internal_end==0x10025d04
 def extent(begin,items):
  position=begin
  for item in items:
   align=item['alignment'];position=(position+align-1)//align*align
   position+=item['bytes']
  return position
 split=max(i for i in range(len(body)+1) if extent(BODY_START,body[:i])<=internal_start)
 before=body[:split];after=body[split:]
 assert extent(internal_end,after)<=TAIL_START
 ld=a.output/'resident-fixed-tail.ld'
 ld.write_text('SECTIONS {\n'+f' {rows[0][0]} 0x{START:08x} : {{ *({rows[0][2]}) }}\n'+f' .gx8002_resident_body_pre 0x{BODY_START:08x} : {{\n'+''.join('  *('+r['section']+')\n' for r in before)+' }\n'+''.join(f' {out} 0x{addr:08x} : {{ *({src}) }}\n' for out,addr,src in rows[1:4])+f' .gx8002_resident_body_post 0x{internal_end:08x} : {{\n'+''.join('  *('+r['section']+')\n' for r in after)+' }\n'+''.join(f' {out} 0x{addr:08x} : {{ *({src}) }}\n' for out,addr,src in rows[4:])+'}\n'+f'ASSERT(ADDR(.gx8002_resident_body_pre)+SIZEOF(.gx8002_resident_body_pre)<=0x{internal_start:08x}, "resident pre-body overlaps clock data")\n'+f'ASSERT(ADDR(.gx8002_resident_body_post)+SIZEOF(.gx8002_resident_body_post)<=0x{TAIL_START:08x}, "resident post-body overlaps stock tail")\n')
 obj=a.output/'resident-fixed-tail.o';cmd=['docker','run','--rm','--network=none','--read-only','--platform','linux/amd64','--mount',f'type=bind,src={TOOL},dst=/tool,readonly','--mount',f'type=bind,src={ROOT},dst=/repo,readonly','--mount',f'type=bind,src={a.output.resolve()},dst=/out','--tmpfs','/tmp:rw','opencfw/iar-base:10.10.2-local','/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-r','-Wl,-A,ck803',f'-Wl,-T,/out/{ld.name}',f'/repo/{a.candidate.resolve().relative_to(ROOT)}','-o',f'/out/{obj.name}'];done=subprocess.run(cmd,capture_output=True,text=True)
 out={'candidate_sha256':sha,'link_exit':done.returncode,'link_stderr':done.stderr[-1500:],'fixed_source_sections':len(rows),'resident_body_sections':len(body),'resident_body_raw_bytes':sum(r['bytes'] for r in body),'body_start':hex(BODY_START),'tail_start':hex(TAIL_START),'stock_end':hex(END)}
 if done.returncode==0:
  t=subprocess.check_output([str(RD),'-SW',str(obj)],text=True)
  def placed(name):
   m=re.search(r'\.'+name+r'\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)',t);assert m,name
   return tuple(int(v,16) for v in m.groups())
  pre_addr,pre_size=placed('gx8002_resident_body_pre')
  post_addr,post_size=placed('gx8002_resident_body_post')
  assert pre_addr==BODY_START and pre_addr+pre_size<=internal_start
  assert post_addr==internal_end and post_addr+post_size<=TAIL_START
  out.update({'body_pre_sections':len(before),'body_pre_end_exclusive':hex(pre_addr+pre_size),'internal_fixed_data_start':hex(internal_start),'internal_fixed_data_end_exclusive':hex(internal_end),'body_post_sections':len(after),'body_post_end_exclusive':hex(post_addr+post_size),'margin_before_internal_data_bytes':internal_start-pre_addr-pre_size,'margin_before_fixed_tail_bytes':TAIL_START-post_addr-post_size,'placed_sha256':hashlib.sha256(obj.read_bytes()).hexdigest()})
 (a.output/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
 if done.returncode:raise SystemExit(done.returncode)
if __name__=='__main__':main()
