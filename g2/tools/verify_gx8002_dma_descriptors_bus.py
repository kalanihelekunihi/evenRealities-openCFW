# SPDX-License-Identifier: MIT
import json
from verify_gx8002_dma_descriptors import verify as descriptors,ROOT,decode
from verify_gx8002_dma_bus_address import verify as bus_verify,execute as bus_execute

def verify():
    dependency=bus_verify();code=decode((ROOT/'build/gx8002-dma-bus-address/bus_address.disassembly.txt').read_text());calls=0
    def hook(address):
        nonlocal calls
        result=bus_execute(code,0x10203c60,address)
        wanted=address&0xfffffff if 0x10000000<=address<0x30000000 else address
        if result!=wanted:raise ValueError('Descriptor bus mapping')
        calls+=1;return result
    result=descriptors(bus_hook=hook)
    return {'descriptor_dependency':result,'bus_dependency':dependency,'decoded_translation_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Separate decoded bus leaf frame; descriptor stock/source use the byte-identical compiled translator. No physical DMA proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-descriptors-bus.json').write_text(json.dumps(result,indent=2)+'\n');print('Descriptor translation calls:',result['decoded_translation_calls'])
