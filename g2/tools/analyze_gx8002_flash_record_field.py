# SPDX-License-Identifier: MIT
"""Authenticated candidate-read inventory for unresolved flash record +12."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,sha
from build_transparent_image import Elf32

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');objects=[]
    for name in ('flash_spi.o','generic_spi_nor.o','spi_nor_ids.o'):
        rel='drivers_lib/mtd/spinor/'+name;path=sdk/rel;blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(path,blob);elf=Elf32(data,name);hits=[]
        listing=subprocess.check_output([pre,'-dr',str(path)],text=True);section=None;symbol=None
        for line in listing.splitlines():
            match=re.match(r'Disassembly of section (.*):',line)
            if match:section=match[1]
            match=re.match(r'[0-9a-f]+ <(.*)>:',line)
            if match:symbol=match[1]
            if re.search(r'ld\.w\s+r\d+, \(r\d+, 0xc\)',line):hits.append({'section':section,'symbol':symbol,'instruction':line.strip()})
        objects.append({'path':rel,'blob':blob,'sha256':sha(data),'candidate_reads':hits})
    return {'sdk_commit':SDK_COMMIT,'objects':objects,'source_admitted':False,'limits':['Offset12 reads are candidates only: base register may be runtime state, stack, MMIO or a different structure. No field meaning or unused-field proof inferred. SDK chip-erase wrapper loads runtime size at+4 and delegates range erase, so does not resolve record+12. Trace record pointer origins and all indirect consumers next.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-flash-record-field-candidates.json').write_text(json.dumps(r,indent=2)+'\n');print([(o['path'],len(o['candidate_reads'])) for o in r['objects']])
