# SPDX-License-Identifier: MIT
"""Read-only shared literal consumers and active queue RAM allocation audit."""
import json,re,subprocess
from compare_gx8002_clear_bss import execute as clear_execute
from verify_gx8002_memcpy_source import decode
from build_gx8002_active_snpu_split import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    disasm=subprocess.check_output([pre,'-D','--start-address=0x15514','--stop-address=0x18d40',str(wrapper)],text=True)
    consumers=[]
    for line in disasm.splitlines():
        if re.search(r'\blrw\b.*//\s*184e8\b',line):
            address=int(line.split(':')[0].strip(),16);assert '0x2002e6ec' in line
            consumers.append(address)
    assert 0x1835c in consumers and len(consumers)>1
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text();overlaps=[];missing=[];checked=0
    for kind,artifact in re.findall(r"\('([^']+)',\s*\w+,\s*'([^']+)',\s*'gx8002-[^']+\.json'\)",registry):
        if kind=='active-snpu':continue
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact
        if not path.exists():missing.append(kind);continue
        image=Elf32(path.read_bytes(),str(path));checked+=1
        for s in image.sections:
            if s['flags']&2 and s['size'] and s['address'] and s['address']<0x2002e738 and 0x2002e6ec<s['address']+s['size']:
                overlaps.append({'kind':kind,'section':s['name'],'address':s['address'],'bytes':s['size']})
    clear_report=json.loads((ROOT/'docs/research/gx8002-clear-bss-verification.json').read_text());clear=clear_report['evidence']['build']
    clear_path=ROOT/'build/gx8002-clear-bss/clear.elf';clear_elf=Elf32(clear_path.read_bytes(),'clear');row=clear_report['functions'][0];section=next(s for s in clear_elf.sections if s['name']==row['section_name']);assert sha(clear_elf.contents(section))==row['compiled_sha256']
    trace=clear_execute(decode(subprocess.check_output([pre,'-d',str(clear_path)],text=True)),section['address'],91)
    assert trace==[[a,0] for a in range(clear['bss_start'],clear['bss_end'],4)]
    cleared=dict(trace);assert all(cleared[a]==0 for a in range(0x2002e6ec,0x2002e738,4))
    assert clear['bss_start']<=0x2002e6ec<0x2002e738<=clear['bss_end']
    return {'startup_clear_elf_sha256':sha(clear_path.read_bytes()),'candidate':evidence,'direct_literal_consumer_package_offsets':consumers,'scan_interval':[0x15514,0x18d40],'queue_region':{'address':0x2002e6ec,'bytes':76,'queue_bytes':20,'buffer_bytes':56},'checked_artifacts':checked,'missing_artifacts':missing,'overlapping_allocations':overlaps,'source_admitted':False,'limits':['Direct disassembly references only; not exhaustive indirect-consumer discovery. Source literal preserves stock value for all consumers. Source queue and buffer BSS allocations are checked by builder; authenticated decoded startup clears every word. Retained indirect writers and concurrency remain outside audit.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-active-snpu-ownership.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ('direct_literal_consumer_package_offsets','checked_artifacts','missing_artifacts','overlapping_allocations')})
