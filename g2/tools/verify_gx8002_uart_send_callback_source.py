# SPDX-License-Identifier: MIT
"""Admit the pinned upstream UART transmit state machine."""
import json,shutil
from verify_gx8002_uart_send_callback import verify as compare
from verify_gx8002_uart_send_callback_mutations import verify as mutations
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();mutation=mutations();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-uart-send-callback/callback.elf';elf=Elf32(path.read_bytes(),'callback')
    text=next(s for s in elf.sections if s['name']=='.text')
    if text['address']!=0x10207f08 or not candidate['fits']:raise ValueError('Placement')
    if sha(elf.contents(text))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'callback.elf')
    files=('verify_gx8002_uart_send_callback_source.py','verify_gx8002_uart_send_callback.py','verify_gx8002_uart_send_callback_mutations.py','execute_gx8002_uart_send_callback.py','build_gx8002_uart_send_callback.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'open_cfw_gx8002_uart_send_callback','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_uart_send_callback','package_offset':0x11494,'bytes':400,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'evidence':evidence,'mutations':mutation,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'source_admitted':True,'hardware_qualified':False,
      'limits':['Pinned upstream source compiled natively; complete finite decoded state-machine checks against independent oracle, helper mutation, rejected ports and saved ABI. Helpers modeled; arbitrary aliasing, concurrency, physical UART and timing remain unqualified. Nonterminating unknown-state behavior observed under instruction bound. External RAM counters are referenced at established addresses; no flash ownership is claimed for them.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-send-callback-source-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Transmit state machine source qualification passed')
