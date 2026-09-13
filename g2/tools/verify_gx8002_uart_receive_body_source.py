# SPDX-License-Identifier: MIT
"""Admit pinned upstream UART receive-body implementation at its original entry."""
import json,shutil
from compare_gx8002_uart_body_full import verify as compare
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare(original_entry=True)
    path=ROOT/'build/gx8002-uart-body-probe/body-candidate.elf';elf=Elf32(path.read_bytes(),'receive body')
    allocated=[s for s in elf.sections if s['flags']&2]
    if {s['name'] for s in allocated}!={'.text','.bss'}:raise ValueError('Unexpected allocation')
    text=next(s for s in allocated if s['name']=='.text');bss=next(s for s in allocated if s['name']=='.bss')
    if text['address']!=0x10207cec or bss['address']!=0x2002e358 or bss['size']!=8 or bss['type']!=8:raise ValueError('Section placement')
    if any(elf.relocations(s['index']) for s in elf.sections):raise ValueError('Relocations')
    payload=elf.contents(text);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or len(payload)>500 or sha(payload)!=evidence['probe']['candidate_sha256']:raise ValueError('Payload identity')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'body.elf')
    files=('verify_gx8002_uart_receive_body_source.py','compare_gx8002_uart_body_full.py','execute_gx8002_uart_body_full.py','build_gx8002_uart_body_upstream_probe.py','verify_gx8002_memcpy_source.py')
    return {'functions':[{'symbol':'open_cfw_gx8002_uart_body_probe','section_name':'.text','compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{'symbol':'open_cfw_gx8002_uart_body_probe','package_offset':0x11278,'bytes':500,'sha256':sha(stock[0x11278:0x1146c]),'region':'image_a_xip_text'}]}],
      'evidence':evidence,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'source_admitted':True,'hardware_qualified':False,
      'limits':['Pinned upstream source compiled natively; 7776 complete decoded cases include decoded source lookup, helper failures and registration rejection. Receive counters are source-declared zero-initialized BSS at existing RAM addresses, not a flash replacement. UART/queue helpers remain modeled in this admission run; finite valid buffer cases do not qualify arbitrary aliasing, concurrency or physical reception.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-body-source-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Receive body source qualification passed')
