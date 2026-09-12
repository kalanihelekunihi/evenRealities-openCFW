# SPDX-License-Identifier: MIT
"""Qualify and export reconstructed DMA channel selection for source admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_select import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from verify_gx8002_dma_select_gate import verify as gate


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    qualification=core();clock=json.loads(json.dumps(gate()));candidate=qualification['candidate'];item=candidate['functions'][0]
    if not item['fits']:raise ValueError('DMA selection envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-select/select.elf',output/'select.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_select.py','verify_gx8002_dma_select.py','verify_gx8002_dma_select_source.py','verify_gx8002_memcpy_source.py','verify_gx8002_dma_select_gate.py','compare_gx8002_platform_gate.py')}
    return {'functions':[row],'qualification':qualification,'clock_composition':clock,'evidence_sha256':evidence,
        'source_admitted':True,'hardware_qualified':False,
        'limits':['Finite channel scan and allocation state checks, IRQ token preservation and separate decoded clock-gate composition. Occupancy counts beyond two are arithmetic tests; physical concurrency and shared gate state remain unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-select-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA selection source qualification passed')
