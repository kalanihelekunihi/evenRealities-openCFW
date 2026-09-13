# SPDX-License-Identifier: MIT
"""Authenticate existing source-owned SNPU callback BSS and lifecycle code."""
import json
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha

def verify():
    owners={}
    for kind,artifact in (('stream-shutdown','stream-shutdown.elf'),('kws-initialize','init.elf')):
        path=ROOT/'build/gx8002-source-candidate'/kind/artifact
        report_path=ROOT/f'docs/research/gx8002-{kind}-verification.json';report=json.loads(report_path.read_text());elf=Elf32(path.read_bytes(),kind)
        for row in report['functions']:
            section=next(s for s in elf.sections if s['name']==row['section_name'])
            assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
        if kind=='stream-shutdown':
            bss=next(s for s in elf.sections if s['name']=='.bss.callback')
            assert bss['type']==8 and bss['address']==0x20027b50 and bss['size']==4
            symbol=next(s for s in elf.symbols() if s['name']=='open_cfw_gx8002_snpu_callback')
            assert symbol['value']==0x20027b50 and symbol['section']==bss['index']
        owners[kind]={'elf_sha256':sha(path.read_bytes()),'report_sha256':sha(report_path.read_bytes())}
    return {'callback_slot':0x20027b50,'bss_symbol':'open_cfw_gx8002_snpu_callback','owners':owners,'source_admitted':False,'limits':['Existing registered source BSS and lifecycle instruction hashes authenticated; no duplicate storage should be introduced. Callback values at runtime remain external inputs; lifecycle/wrapper shared-memory composition pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-completion-owner.json').write_text(json.dumps(r,indent=2)+'\n');print(hex(r['callback_slot']))
