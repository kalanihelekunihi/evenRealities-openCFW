#!/usr/bin/env python3
"""Packed relocatable size probe for source XIP relocation closure."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
TOOL=ROOT/'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'
READELF=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
START=0x10203004;CAPACITY=36484

def xip_section(name):
 if name=='.text' or name.startswith(('.text.gx8002_resident_','.rodata.gx8002_resident_')) and '10203c74' not in name:return False
 if name.startswith('.gx8002.') and not name.startswith(('.gx8002.sample_name.','.gx8002.flash_name.','.gx8002.xip.')):return False
 return True

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--closure',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 closure=json.loads(a.closure.read_text());sha=hashlib.sha256(a.candidate.read_bytes()).hexdigest();assert closure['candidate_sha256']==sha
 secs=[s for s in closure['xip_relocation_closure']['sections'] if xip_section(s['section'])]
 linker=a.output/'xip-closure-probe.ld'; linker.write_text('SECTIONS {\n .gx8002_xip_closure 0x10203004 : {\n'+''.join('  *('+s['section']+')\n' for s in secs)+' }\n}\n')
 placed=a.output/'xip-closure-probe.o'
 cmd=['docker','run','--rm','--network=none','--read-only','--platform','linux/amd64','--mount',f'type=bind,src={TOOL},dst=/tool,readonly','--mount',f'type=bind,src={ROOT},dst=/repo,readonly','--mount',f'type=bind,src={a.output.resolve()},dst=/out','--tmpfs','/tmp:rw','opencfw/iar-base:10.10.2-local','/tool/bin/csky-abiv2-elf-gcc','-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles','-Wl,-r','-Wl,-A,ck803',f'-Wl,-T,/out/{linker.name}',f'/repo/{a.candidate.resolve().relative_to(ROOT)}','-o',f'/out/{placed.name}']
 subprocess.run(cmd,check=True)
 lines=subprocess.check_output([str(READELF),'-SW',str(placed)],text=True).splitlines();match=next(re.search(r'\[\s*\d+\]\s+\.gx8002_xip_closure\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)',line) for line in lines if '.gx8002_xip_closure' in line)
 start,size=(int(v,16) for v in match.groups());assert start==START
 out={'candidate_sha256':sha,'closure_sha256':hashlib.sha256(a.closure.read_bytes()).hexdigest(),'linker_sha256':hashlib.sha256(linker.read_bytes()).hexdigest(),'placed_sha256':hashlib.sha256(placed.read_bytes()).hexdigest(),'selected_sections':len(secs),'selected_raw_bytes':sum(s['bytes'] for s in secs),'packed_with_alignment_bytes':size,'native_xip_capacity_bytes':CAPACITY,'excess_bytes':size-CAPACITY,'start':hex(start),'end_exclusive':hex(start+size),'limits':['This is a section placement probe for relocation-reachable source sections classified as XIP using authenticated native region identity.','It does not admit native/runtime equality or prove external package extension.','Indirectly referenced, non-closure sections, veneers and final loader metadata may increase size.']}
 (a.output/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
if __name__=='__main__':main()
