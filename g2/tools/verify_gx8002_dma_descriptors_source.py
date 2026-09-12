# SPDX-License-Identifier: MIT
"""Export qualified recovered descriptor construction for experimental admission."""
import json,shutil
from pathlib import Path
from verify_gx8002_dma_descriptors import verify as core,ROOT,sha
from verify_gx8002_dma_configure_descriptors import verify as composition
from verify_gx8002_dma_bus_address import verify as bus_verify,execute as bus
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    dependency=bus_verify()
    code=decode((ROOT/'build/gx8002-dma-bus-address/bus_address.disassembly.txt').read_text())
    qualification=core(bus_hook=lambda address:bus(code,0x10203c60,address))
    composed=composition();item=qualification['candidate']['functions'][0]
    if not item['fits'] or item['additional_source_data_sections']:raise ValueError('Descriptor code/data envelope')
    row={key:item[key] for key in ('symbol','compiled_bytes','compiled_sha256')}
    row['section_name']='.text'
    row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],
        'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output=Path(output);output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-dma-descriptors/descriptors.elf',output/'descriptors.elf')
    evidence={name:sha((ROOT/'tools'/name).read_bytes()) for name in
        ('build_gx8002_dma_descriptors.py','verify_gx8002_dma_descriptors.py','execute_gx8002_dma_descriptors.py',
         'verify_gx8002_dma_descriptors_source.py','verify_gx8002_dma_configure_descriptors.py',
         'verify_gx8002_dma_configure.py','execute_gx8002_dma_configure.py','verify_gx8002_memcpy_source.py')}
    return {'functions':[row],'qualification':qualification,'configuration_composition':composed,
        'bus_dependency':dependency,'evidence_sha256':evidence,'source_admitted':True,'hardware_qualified':False,
        'limits':['Finite decoded construction corpus with source bus translation and independent configure/descriptor address and flag checks. Separate execution frames; physical DMA and concurrent descriptor use not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-descriptors-source-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('DMA descriptors source qualification passed')
