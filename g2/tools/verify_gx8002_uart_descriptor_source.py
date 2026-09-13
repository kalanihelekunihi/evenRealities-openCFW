# SPDX-License-Identifier: MIT
"""Experimental admission gate for source-authored UART descriptor defaults."""
import json,shutil
from verify_gx8002_uart_descriptor_mapping import verify as mapping
from verify_gx8002_uart_descriptor_clear import verify as clear
from verify_gx8002_uart_descriptor_placement import verify as placement
from verify_gx8002_uart_descriptor_defaults import verify as defaults
from verify_gx8002_uart_defaults_initialize import verify as initialize
from build_gx8002_uart_descriptor_candidate import ROOT,sha,Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'mapping':mapping(),'clear':clear(),'placement':placement(),'defaults':defaults(),'initialize':initialize()}
    path=ROOT/'build/gx8002-board/uart-descriptor.elf';elf=Elf32(path.read_bytes(),'UART');allocated=[s for s in elf.sections if s['flags']&2 and s['size']];assert len(allocated)==1
    section=allocated[0];body=elf.contents(section);stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    assert section['name']=='.descriptors' and section['address']==0x20026a94 and len(body)==256 and body==stock[0x18aa8:0x18ba8]
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section']==0 for s in elf.symbols())
    symbol='open_cfw_gx8002_uart_descriptors'
    row={'symbol':symbol,'section_name':'.descriptors','ownership_kind':'generated_source_data','compiled_bytes':256,'compiled_sha256':sha(body),'stock_occurrences':[{'symbol':symbol,'package_offset':0x18aa8,'bytes':256,'sha256':sha(body),'region':'image_a_sram'}]}
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'descriptors.elf')
    files=sorted({p.name for p in (ROOT/'tools').glob('*gx8002_uart_descriptor*.py')} | {'verify_gx8002_uart_defaults_initialize.py','verify_gx8002_uart_loader_setup.py','verify_gx8002_uart_initialize.py','verify_gx8002_uart_configure.py','execute_gx8002_uart_configure.py','verify_gx8002_memcpy_source.py','compare_gx8002_clear_bss.py','analyze_gx8002_gsensor_state_references.py'})
    return {'functions':[row],'checks':checks,'evidence_sha256':{n:sha((ROOT/'tools'/n).read_bytes()) for n in files},'source_admitted':True,'hardware_qualified':False,'unresolved_semantics':['Original names of descriptor fields7/8 remain unknown; source preserves defaults8/1. Configuration behavior is bounded by decoded checks; this does not establish whole-program non-use.'],'limits':['Experimental hybrid data admission; C initializer uses SDK UART bases/IRQs and recovered defaults, with binary used only as comparison evidence.','Primary flash transfer and physical IRAM/DRAM alias modeled, peripheral helpers modeled. This admission does not satisfy the complete no-opacity goal.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-descriptor-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('UART descriptor admission gate passed; semantics remain unresolved')
