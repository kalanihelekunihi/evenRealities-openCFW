# SPDX-License-Identifier: MIT
"""Aggregate clock-frequency source evidence and export qualified sections."""
import json
import shutil
from pathlib import Path
from verify_gx8002_clock_stock_continuous import verify as low
from verify_gx8002_clock_stock_high import verify as high
from verify_gx8002_clock_stock_pll import verify as pll
from analyze_gx8002_clock_table_host_flow import analyze_flow
from verify_gx8002_clock_table_partition import verify as partition
from analyze_gx8002_upstream_objects import IMAGE,sha
from link_gx8002_uart_console import ROOT
from build_transparent_image import Elf32
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    checks={'low':low(),'high':high(),'pll':pll(),'host_flow':analyze_flow(),'partition':partition()}
    artifact=ROOT/'build/gx8002-clock-frequency-table-probe/placement.elf'
    elf=Elf32(artifact.read_bytes(),'clock frequency provider');stock=IMAGE.read_bytes();rows=[]
    for symbol,section_name,offset,size,kind in (
        ('open_cfw_gx8002_clock_frequency','.text.open_cfw_gx8002_clock_frequency',0x17224,444,'compiled_c'),
        ('open_cfw_gx8002_clock_frequency_dispatch','.rodata.open_cfw_gx8002_clock_frequency',0x17474,76,'generated_source_data'),
        ('open_cfw_gx8002_clock_subband_hz','.rodata.subband_hz',97868,16,'generated_source_data')):
        sec=next(s for s in elf.sections if s['name']==section_name);payload=elf.contents(sec)
        if len(payload)!=size or elf.relocations(sec['index']):raise ValueError('Frequency provider section')
        rows.append({'symbol':symbol,'section_name':section_name,'compiled_bytes':size,'compiled_sha256':sha(payload),
            'ownership_kind':kind,'stock_occurrences':[{'symbol':symbol,'package_offset':offset,'bytes':size,
            'sha256':sha(stock[offset:offset+size]),'region':'image_a_sram_text'}]})
    names=('verify_gx8002_clock_frequency_source.py','verify_gx8002_clock_stock_continuous.py','verify_gx8002_clock_stock_high.py',
        'verify_gx8002_clock_stock_pll.py','verify_gx8002_clock_low_frame.py','decode_gx8002_stock_clock.py',
        'analyze_gx8002_clock_table_host_flow.py','verify_gx8002_clock_table_partition.py','gx8002_source_tail_data.py',
        'analyze_gx8002_clock_table_placement.py','link_gx8002_clock_frequency_table_probe.py',
        'probe_gx8002_clock_frequency_table_size.py','build_gx8002_clock_frequency_candidate.py',
        'link_gx8002_clock_frequency_candidate.py','model_gx8002_clock_pll_frequency.py','build_gx8002_platform_config.py','build_gx8002_clock_divider_candidate.py',
        'verify_gx8002_memcpy_source.py','verify_gx8002_padmux_get.py','analyze_gx8002_upstream_objects.py','build_transparent_image.py')
    pins={name:sha((ROOT/'tools'/name).read_bytes()) for name in names}
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True);shutil.copyfile(artifact,output/'clock-frequency.elf')
    return {'functions':rows,'checks':checks,'evidence_sha256':pins,'source_admitted':True,'hardware_qualified':False,
        'tail_allocation':{'host_symbol':'open_cfw_gx8002_platform_config','host_stock_sha256':checks['partition']['placement']['host_stock_sha256'],'data_symbol':'open_cfw_gx8002_clock_subband_hz'},
        'limits':['650 continuous stock/source cases with actual tables, helper bodies, frames and ordered MMIO. Finite fixed register scenarios; dynamic MMIO, hardware timing and full-image qualification not established. Experimental source admission within this scope.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-frequency-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Clock source evidence:',len(report['functions']),'sections')
