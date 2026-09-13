# SPDX-License-Identifier: MIT
"""Use compiled address translation in backup descriptor/configuration tests."""
import json
from build_gx8002_backup_dma_bus_address import ROOT, build, Elf32, sha
from verify_gx8002_backup_dma_bus_address import execute as translate
from verify_gx8002_backup_dma_descriptors import verify as descriptors
from verify_gx8002_backup_dma_configure import verify as configure
from verify_gx8002_memcpy_source import decode


def verify():
    evidence=build();path=ROOT/'build/gx8002-backup-dma-bus-address/bus_address.elf'
    elf=Elf32(path.read_bytes(),str(path));section=next(s for s in elf.sections if s['name']=='.text')
    assert sha(elf.contents(section))==evidence['functions'][0]['compiled_sha256']
    code=decode((ROOT/'build/gx8002-backup-dma-bus-address/bus_address.disassembly.txt').read_text())
    calls=0
    def hook(address):
        nonlocal calls
        calls+=1
        value=translate(code,0x100051c4,address)
        assert value==(address&0x0fffffff if 0x10000000<=address<0x30000000 else address)
        return value
    descriptor_report=descriptors(bus_hook=hook)
    configure_report=configure(bus_hook=hook)
    result={'translation_build':evidence,'descriptor_cases':descriptor_report['decoded_cases'],
            'configuration_cases':configure_report['decoded_cases'],
            'compiled_translation_calls':calls,'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled translation supplies helper return values to both stock and source instruction executions.',
                      'Descriptor/configuration frames remain separately modeled; configuration descriptor helper and physical DMA remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dma-translation-composition.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
