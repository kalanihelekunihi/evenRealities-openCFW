# SPDX-License-Identifier: MIT
"""Apply authenticated section/alias evidence to all UART descriptor words."""
import json
from build_gx8002_uart_descriptor_candidate import build,ROOT,sha,Elf32
from analyze_gx8002_gsensor_state_references import mapped_offset,section_map,SDK_EVIDENCE
from verify_gx8002_uart_descriptor_loader import verify as loader_arguments
from verify_gx8002_uart_loader_setup import verify as loader_setup

def verify():
    evidence=build();layout=section_map();sdk=ROOT/'build/upstream-nationalchip-lvp-kws';words=[]
    for i in range(64):
        address=0x20026a94+4*i;offset=mapped_offset(address,layout,sdk);assert offset==0x18aa8+4*i;words.append({'dram':address,'package_offset':offset})
    arguments=loader_arguments();setup=loader_setup();assert arguments['uart_destination_iram']+0x10000000==words[0]['dram']
    path=ROOT/'build/gx8002-board/uart-descriptor.elf';elf=Elf32(path.read_bytes(),'UART');section=next(s for s in elf.sections if s['name']=='.descriptors');assert section['address']==words[0]['dram'] and section['size']==len(words)*4
    return {'candidate':evidence,'sdk_mapping_sha256':SDK_EVIDENCE,'word_mapping':words,'loader_arguments':arguments,'loader_setup':setup,'source_admitted':False,'limits':['All UART words mapped using existing authenticated stock section and SDK IRAM/DRAM evidence; decoded primary loader destination agrees. This is source/static-model evidence, not physical alias or flash-transfer measurement. Fields7/8 semantic names remain unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-descriptor-mapping.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['word_mapping']))
