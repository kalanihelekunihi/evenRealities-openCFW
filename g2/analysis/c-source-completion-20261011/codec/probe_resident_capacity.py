#!/usr/bin/env python3
"""Pack image-A native-address resident sections as a stage-2 SRAM size test."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
TOOL=ROOT/'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
RD=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
START=0x10023400;CAPACITY=14716

def resident(n):
 if n=='.text':return True
 if n.startswith(('.text.gx8002_resident_','.rodata.gx8002_resident_')) and '10203c74' not in n:return True
 if n.startswith('.gx8002.') and not n.startswith(('.gx8002.sample_name.','.gx8002.flash_name.','.gx8002.xip.')):return True
 return False

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 closure=json.loads(a.closure.read_text());sha=hashlib.sha256(a.candidate.read_bytes()).hexdigest();assert sha==closure['candidate_sha256']
 secs=[s for s in closure['all_alloc_progbits']['sections'] if resident(s['section'])]
 ld=a.output/'resident-capacity-probe.ld';ld.write_text('SECTIONS {\n .gx8002_resident_packed 0x10023400 : {\n'+''.join('  *('+s['section']+')\n' for s in secs)+' }\n}\n')
 obj=a.output/'resident-capacity-probe.o';cmd=['docker','run','--rm','--network=none','--read-only','--platform','linux/amd64','--mount',f'type=bind,src={TOOL},dst=/tool,readonly','--mount',f'type=bind,src={ROOT},dst=/repo,readonly','--mount',f'type=bind,src={a.output.resolve()},dst=/out','--tmpfs','/tmp:rw','opencfw/iar-base:10.10.2-local','/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-r','-Wl,-A,ck803',f'-Wl,-T,/out/{ld.name}',f'/repo/{a.candidate.resolve().relative_to(ROOT)}','-o',f'/out/{obj.name}'];subprocess.run(cmd,check=True)
 t=subprocess.check_output([str(RD),'-SW',str(obj)],text=True);m=re.search(r'\.gx8002_resident_packed\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)',t);assert m;start,size=(int(v,16) for v in m.groups());assert start==START
 out={'candidate_sha256':sha,'section_count':len(secs),'raw_bytes':sum(s['bytes'] for s in secs),'packed_bytes':size,'native_stage2_sram_source_bytes':CAPACITY,'excess_bytes':size-CAPACITY,'start':hex(start),'end_exclusive':hex(start+size),'limits':['Classifies only native-address/pinned resident sections; helper code and other runtime data may add demand.','No final copy, BSS, heap, stack or branch reach is proven by this relocatable link.']}
 (a.output/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
