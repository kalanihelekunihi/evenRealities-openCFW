# SPDX-License-Identifier: MIT
"""Admit the pinned upstream UART registration routine."""
import json,shutil
from verify_gx8002_uart_message_done import verify as compare
from verify_gx8002_uart_message_done_fill import verify as fill_verify
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();fill=fill_verify();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-uart-message-done/callback.elf';elf=Elf32(path.read_bytes(),'callback')
    text=next(s for s in elf.sections if s['name']=='.text')
    if text['address']!=0x1020854c or not candidate['fits']:raise ValueError('Placement')
    if sha(elf.contents(text))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'callback.elf')
    files=('verify_gx8002_uart_message_done_fill.py','compare_gx8002_memset.py','build_gx8002_memset_candidate.py','verify_gx8002_uart_message_done_source.py','verify_gx8002_uart_message_done.py','execute_gx8002_uart_message_done.py','build_gx8002_uart_message_done.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'UartMessageAsyncDone','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'UartMessageAsyncDone','package_offset':0x11ad8,'bytes':88,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'evidence':evidence,'fill_composition':fill,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'source_admitted':True,'hardware_qualified':False,
      'limits':evidence['limits']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-message-done-source-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Registration routine source qualification passed')
