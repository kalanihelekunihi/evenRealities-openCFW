# SPDX-License-Identifier: MIT
"""Admit the pinned upstream UART registration routine."""
import json,shutil
from verify_gx8002_uart_message_initialize import verify as compare
from verify_gx8002_uart_message_initialize_mutations import verify as mutations
from verify_gx8002_uart_message_initialize_queue import verify as queue_verify
from verify_gx8002_uart_message_initialize_power import verify as power_verify
from verify_gx8002_logging import check_paths
from analyze_gx8002_upstream_objects import ROOT,IMAGE,sha
from build_transparent_image import Elf32

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=compare();mutation=mutations();queue=queue_verify();power=power_verify();candidate=evidence['candidate']
    path=ROOT/'build/gx8002-uart-message-initialize/callback.elf';elf=Elf32(path.read_bytes(),'callback')
    text=next(s for s in elf.sections if s['name']=='.text')
    if text['address']!=0x10208458 or not candidate['fits']:raise ValueError('Placement')
    if sha(elf.contents(text))!=candidate['compiled_sha256']:raise ValueError('Payload')
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'callback.elf')
    files=('verify_gx8002_uart_message_initialize_power.py','compare_gx8002_power_registration.py','link_gx8002_suspend_registration.py','verify_gx8002_queue_source.py','verify_gx8002_uart_message_initialize_mutations.py','verify_gx8002_uart_message_initialize_queue.py','compare_gx8002_queue_put.py','compare_gx8002_queue_get.py','verify_gx8002_uart_message_initialize_source.py','verify_gx8002_uart_message_initialize.py','execute_gx8002_uart_message_initialize.py','build_gx8002_uart_message_initialize.py','verify_gx8002_memcpy_source.py','verify_gx8002_power_initialize.py')
    return {'functions':[{'symbol':'UartMessageAsyncInit','section_name':'.text','compiled_bytes':candidate['compiled_bytes'],'compiled_sha256':candidate['compiled_sha256'],'stock_occurrences':[{'symbol':'UartMessageAsyncInit','package_offset':0x119e4,'bytes':244,'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]}]+[{'symbol':row['symbol'],'section_name':row['section_name'],'compiled_bytes':row['bytes'],'compiled_sha256':row['sha256'],'ownership_kind':'generated_source_data','stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],'bytes':row['bytes'],'sha256':row['sha256'],'region':'image_a_xip_text'}]} for row in candidate['labels']],
      'evidence':evidence,'mutations':mutation,'queue_composition':queue,'power_composition':power,'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in files},'source_admitted':True,'hardware_qualified':False,
      'limits':['Native upstream C; independent baseline, helper mutation/context aliases and nested queue comparison. Helpers otherwise modeled; physical concurrency, cache effects and arbitrary overlap remain unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-message-initialize-source-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Registration routine source qualification passed')
