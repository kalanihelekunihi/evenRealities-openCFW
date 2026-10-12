#!/usr/bin/env python3
"""Conditional source-only executable relocation/segment probe for image A."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT / 'g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain'

p = argparse.ArgumentParser()
p.add_argument('--candidate', type=Path, required=True)
p.add_argument('--script', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
elf = a.output / 'source-only-layout.elf'
cmd = ['docker','run','--rm','--network=none','--read-only','--platform','linux/amd64',
       '--mount',f'type=bind,src={TOOL},dst=/tool,readonly',
       '--mount',f'type=bind,src={ROOT},dst=/repo,readonly',
       '--mount',f'type=bind,src={a.output.resolve()},dst=/out','--tmpfs','/tmp:rw',
       'opencfw/iar-base:10.10.2-local','/tool/bin/csky-abiv2-elf-gcc',
       '-mcpu=ck804ef','-mhard-float','-nostdlib','-nostartfiles',
       '-Wl,-e,gx8002_resident_reset_entry_23500',
       '-Wl,-T,/repo/'+str(a.script.resolve().relative_to(ROOT)),
       '-Wl,-Map,/out/source-only-layout.map',
       '/repo/'+str(a.candidate.resolve().relative_to(ROOT)), '-o','/out/source-only-layout.elf']
r = subprocess.run(cmd, capture_output=True, text=True)
(a.output/'link.stdout').write_text(r.stdout)
(a.output/'link.stderr').write_text(r.stderr)
result={'candidate_sha256':hashlib.sha256(a.candidate.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(a.script.read_bytes()).hexdigest(),
        'link_exit_code':r.returncode,'link_stderr_tail':r.stderr[-4000:],
        'source_only':True,'full_firmware_qualified':False,
        'limits':['Conditional 25-section source-root discard requires native indirect/external root proof.',
                  'Stage-1 package/XIP header emission and physical SRAM/DRAM alias are outside this ELF.',
                  'QEMU/hardware execution and all target literal/branch behavior remain unqualified.']}
if r.returncode == 0:
    def tool(*args):
        c=cmd[:cmd.index('/tool/bin/csky-abiv2-elf-gcc')]+['/tool/bin/csky-abiv2-elf-readelf',*args]
        q=subprocess.run(c,capture_output=True,text=True,check=True)
        return q.stdout
    # Read through the same pinned target toolchain.
    out=[]
    for mode in ('-h','-l','-r','-SW'):
        c=cmd[:cmd.index('/tool/bin/csky-abiv2-elf-gcc')]+['/tool/bin/csky-abiv2-elf-readelf',mode,'/out/source-only-layout.elf']
        q=subprocess.run(c,capture_output=True,text=True,check=True)
        (a.output/('readelf-'+mode[1:]+'.txt')).write_text(q.stdout)
        out.append(q.stdout)
    result['elf_sha256']=hashlib.sha256(elf.read_bytes()).hexdigest()
    result['relocation_table_empty']=('There are no relocations in this file.' in out[2])
    import re
    entry_match=re.search(r'Entry point address:\s*(0x[0-9a-fA-F]+)',out[0])
    assert entry_match
    result['entry_address']=entry_match.group(1)
    result['native_loader_entry_match']=(int(entry_match.group(1),16)==0x10023500)
    sections={}
    for line in out[3].splitlines():
        match=re.search(r'\]\s+(\.gx8002_\S+)\s+(PROGBITS|NOBITS)\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)',line)
        if match: sections[match.group(1)]={'type':match.group(2),'address':int(match.group(3),16),'bytes':int(match.group(4),16)}
    result['key_sections']={k:sections[k] for k in ('.gx8002_vectors','.gx8002_resident_body_pre','.gx8002_resident_body_post','.gx8002_xip_closure','.gx8002_request_initial') if k in sections}
    result['native_region_bounds_match']=(sections.get('.gx8002_vectors',{}).get('address')==0x10023400 and sections.get('.gx8002_request_initial',{}).get('address',0)+sections.get('.gx8002_request_initial',{}).get('bytes',0)==0x10026d7c and sections.get('.gx8002_xip_closure',{}).get('address')==0x10203004 and sections.get('.gx8002_xip_closure',{}).get('address',0)+sections.get('.gx8002_xip_closure',{}).get('bytes',0)<=0x1020be88)
    result['conditional_executable_layout_passed']=result['native_loader_entry_match'] and result['relocation_table_empty'] and result['native_region_bounds_match']
    result['program_headers']=out[1]
(a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='program_headers'},indent=2))
