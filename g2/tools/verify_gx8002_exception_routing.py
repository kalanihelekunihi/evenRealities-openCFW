# SPDX-License-Identifier: MIT
"""Verify exception SRAM placement and registered vector ingress."""
import json,struct,subprocess
from build_gx8002_exception_candidate import build,ROOT,sha,Elf32
from analyze_g2_codec_stage2_sections import analyze,SEG2_OFF
from verify_gx8002_memcpy_source import decode

def verify():
    candidate=build();layout=analyze();region=layout['image_a']['stage2']['sram_text'];assert region['iram']=='[0x10023400, 0x100264E4)'
    delta=0x10023400-(SEG2_OFF+0xbe88)
    p=ROOT/'build/gx8002-exception/exception.elf';elf=Elf32(p.read_bytes(),'exception');symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    for section in candidate['sections']:assert section['address']==section['stock_offset']+delta
    assert symbols['trap']==0x100235fc and symbols['trap_c']==0x100235f0 and symbols['Default_Handler']==0x10023640
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(p)],text=True));assert code[symbols['Default_Handler']][:2]==('br',hex(symbols['trap']))
    p=ROOT/'build/gx8002-source-candidate/application-vectors/vectors.elf'
    if not p.exists():p=ROOT/'build/gx8002-application-vectors/candidate.elf'
    elf=Elf32(p.read_bytes(),'vectors');report=json.loads((ROOT/'docs/research/gx8002-application-vectors-source-verification.json').read_text());row=report['functions'][0];s=next(s for s in elf.sections if s['name']==row['section_name']);data=elf.contents(s);assert sha(data)==row['compiled_sha256']
    words=struct.unpack('<64I',data);assert words[1:32]==(symbols['Default_Handler'],)*31
    return {'candidate':candidate,'vector_elf_sha256':sha(p.read_bytes()),'vector_entries':list(range(1,32)),'default_handler':symbols['Default_Handler'],'trap':symbols['trap'],'source_admitted':False,'limits':['Authenticated SRAM mapping and all31 exception vector entries reach linked Default_Handler branch to trap. Hardware dispatch and nested exceptions remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-exception-routing.json').write_text(json.dumps(r,indent=2)+'\n');print('Exception vector routes:',len(r['vector_entries']))
