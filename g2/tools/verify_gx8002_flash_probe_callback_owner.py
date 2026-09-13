# SPDX-License-Identifier: MIT
"""Authenticate probe callback slot and its separately admitted C entry."""
import json,struct
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import ROOT,sha


def verify():
    evidence={}
    for name,artifact in (('flash-interface-table','flash-interface-table.elf'),('flash-interface-initialize','flash-interface.elf')):
        report_path=ROOT/f'docs/research/gx8002-{name}-verification.json'
        report=json.loads(report_path.read_text());path=ROOT/'build/gx8002-board'/artifact
        elf=Elf32(path.read_bytes(),name);row=report.get('functions',[report])[0];section=next(s for s in elf.sections if s['name']==row['section_name']);data=elf.contents(section)
        assert sha(data)==row['compiled_sha256'] and not elf.relocations(section['index'])
        evidence[name]={'elf_sha256':sha(path.read_bytes()),'report_sha256':sha(report_path.read_bytes()),'address':section['address']}
        if name=='flash-interface-table':
            assert section['address']==0x20026504 and len(data)==120
            target=struct.unpack_from('<I',data)[0]
        else:assert section['address']==target==0x1002443c
    bindings=json.loads((ROOT/'docs/research/gx8002-flash-interface-source-bindings.json').read_text())
    assert bindings[0]['runtime_address']==target and bindings[0]['symbol']=='open_cfw_gx8002_flash_interface_initialize'
    return {'callback_slot':0x20026504,'callback_target':target,'owners':evidence,'source_admitted':False,
            'limits':['Initial callback slot and code source owners authenticated. Runtime replacement pointers remain external input.',
                       'Probe state byte 0x20026ff4 is separate from initialized flash state; BSS ownership and callback execution integration remain pending.']}
if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-flash-probe-callback-owner.json').write_text(json.dumps(report,indent=2)+'\n');print(hex(report['callback_target']))
