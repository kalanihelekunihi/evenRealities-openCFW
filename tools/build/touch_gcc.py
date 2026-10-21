# SPDX-License-Identifier: MIT
"""Reviewed GCC -Og profile for the existing authenticated touch PDL inputs."""
import csv
import json
from pathlib import Path
from source_providers import ROOT, sha


def candidates():
    # Local cache of the official Arm GNU releases listed in touch-gcc-acquisition.json.
    matrix=ROOT/'vendor-cache/g2/touch-gcc-matrix'
    acquired=json.loads((ROOT/'tools/build/touch-gcc-acquisition.json').read_text())
    tool=next(e for e in acquired if e['version']=='12.2.Rel1')
    compiler=matrix/tool['gcc']
    if sha(compiler)!=tool['gcc_sha256']:raise ValueError('touch GCC identity mismatch')
    base=ROOT/'third-party/upstream/psoc4-touch-slice'
    pdl=matrix/'pdl-input'
    includes=[base,base/'cmsis',pdl/'drivers/include',pdl/'devices/include',
              base/'core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include']
    rows=list(csv.DictReader((ROOT/'g2/symbols/touch.tsv').open(),delimiter='\t'))
    anchors=[dict(symbol=r['name'],address=int(r['address'],16),
                  start=int(r['address'],16)-0x3300+32,size=int(r['size'])) for r in rows if r['size']]
    # Earlier section equality receipts establish additional upstream aliases;
    # fresh compilation and equality are still mandatory in the selector.
    evidence=ROOT/'g2/evidence/touch-msclp-unique-exact-sections.json'
    for r in json.loads(evidence.read_text())['matches']:
        if len(r['matches'])!=1:continue
        address=int(r['matches'][0],16)
        anchors.append(dict(symbol=r['function'],address=address,start=address-0x3300+32,size=r['bytes']))
    def relative(path):return str(path).replace(str(ROOT),'{root}')
    flags=['python3','{root}/tools/build/linux_gcc.py','--compiler',relative(compiler),
           '--read-root',relative(base),'--read-root',relative(pdl),'--',
           '-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin',
           '-DCY8C4046FNI_T412','-ffunction-sections','-fdata-sections',
           *['-I'+relative(p) for p in includes]]
    return [dict(source=str(source.relative_to(ROOT)),argv=flags,compiler_path=relative(compiler),
                 compiler_sha256=tool['gcc_sha256'],payload='g2-touch',anchors=anchors,
                 evidence='g2/symbols/touch.tsv; '+str(evidence.relative_to(ROOT)))
            for source in sorted((pdl/'drivers/source').glob('*.c'))]
