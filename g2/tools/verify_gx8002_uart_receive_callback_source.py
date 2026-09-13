# SPDX-License-Identifier: MIT
"""Admit the pinned upstream UART receive state machine."""
import json,shutil
from verify_gx8002_uart_receive_callback import verify as compare
from verify_gx8002_uart_receive_callback_mutations import verify as mutations
from verify_gx8002_uart_receive_callback_body import verify as body_verify
from verify_gx8002_uart_receive_callback_queue import verify as queue_verify
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();mutation=mutations();body=body_verify();queue=queue_verify();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-uart-receive-callback/callback.elf';elf=Elf32(path.read_bytes(),'callback')
    text=next(s for s in elf.sections if s['name']=='.text')
    if text['address']!=0x10208098 or not candidate['fits']:raise ValueError('Placement')
    if sha(elf.contents(text))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'callback.elf')
    files=('gx8002_uart_receive_callback_oracle.py','verify_gx8002_uart_receive_callback_body.py','verify_gx8002_uart_receive_callback_queue.py','execute_gx8002_uart_body_full.py','build_gx8002_uart_body_upstream_probe.py','compare_gx8002_queue_put.py','compare_gx8002_queue_get.py','verify_gx8002_uart_receive_callback_source.py','verify_gx8002_uart_receive_callback.py','verify_gx8002_uart_receive_callback_mutations.py','execute_gx8002_uart_receive_callback.py','build_gx8002_uart_receive_callback.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'open_cfw_gx8002_uart_receive_callback','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'open_cfw_gx8002_uart_receive_callback','package_offset':0x11624,'bytes':532,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}],
      'evidence':evidence,'mutations':mutation,'body_composition':body,'queue_composition':queue,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'source_admitted':True,'hardware_qualified':False,
      'limits':['Pinned upstream source compiled natively; complete finite decoded state-machine checks against independent oracle, helper mutation, rejected ports and saved ABI. Helpers modeled; arbitrary aliasing, concurrency, physical UART and timing remain unqualified. Nested decoded body shares packet/global memory; source queue uses separate translated memory. Store widths/order may differ; final bytes and helper boundaries qualified. External RAM counters are referenced at established addresses; no flash ownership is claimed for them.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-callback-source-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Receive state machine source qualification passed')
