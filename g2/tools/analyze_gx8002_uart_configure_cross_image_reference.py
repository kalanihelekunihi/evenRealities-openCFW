# SPDX-License-Identifier: MIT
"""Characterize the real watchdog pointer aliasing backup UART code space."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_double_wrapper_references import analyze


def analyze_reference():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([tool,'-D','--start-address=0x44a4','--stop-address=0x454c',str(wrapper)],text=True))
    assert int.from_bytes(stock[0x4544:0x4548],'little')==0x10004454
    expected={0x451c:('lrw','r1, 0x10004454'),0x451e:('movi','r0, 11'),0x4522:('bsr','0x3138'),
              0x44a4:('push','r15'),0x44a6:('lrw','r3, 0x20009960'),0x44a8:('ld.w','r3, (r3, 0x0)'),
              0x44ae:('jsr','r3'),0x44b0:('movih','r3, 41072'),0x44b4:('ld.w','r3, (r3, 0x14)')}
    for pc,value in expected.items():assert code[pc][:2]==value,(pc,code[pc],value)
    references=analyze(0x3cce4,0x3ce5c,False)
    assert references['stored_address_words']==[{'offset':0x4544,'value':0x10004454,'entry':False}]
    return {'stock_sha256':IMAGE_SHA,'references':references,'literal_offset':0x4544,'literal_value':0x10004454,
            'literal_reader':0x451c,'registration_call':0x4522,'irq_number':11,'registration_target':0x3138,
            'earlier_image_mapping_candidate':{'delta':0x10000000-0x50,'handler_package_offset':0x44a4},
            'handler_observed_behavior':{'callback_cell':0x20009960,'indirect_call':0x44ae,'watchdog_status_read':0xa0700014},
            'source_admitted':False,'cross_image_lifetime_resolved':False,
            'limits':['The real earlier-image watchdog pointer numerically aliases backup configuration interior code. Reader and handler instructions authenticated. Mapping candidate is consistent with the earlier image layout; loader/lifetime and IRQ table separation still require explicit evidence before dismissing the cross-image alias.']}


if __name__=='__main__':
    result=analyze_reference()
    (ROOT/'docs/research/gx8002-uart-configure-cross-image-reference.json').write_text(json.dumps(result,indent=2)+'\n')
    print('IRQ',result['irq_number'],'watchdog pointer characterized; lifetime remains unresolved')
