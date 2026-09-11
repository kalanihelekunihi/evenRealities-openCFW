# SPDX-License-Identifier: MIT
import json,subprocess
from verify_gx8002_dma_configure import verify as configure,ROOT,decode
from verify_gx8002_dma_descriptors import verify as descriptors_verify
from execute_gx8002_dma_descriptors import execute

def verify():
    dependency=descriptors_verify();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcdb4','--stop-address=0xce80',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-dma-descriptors/descriptors.disassembly.txt').read_text());calls=0
    def hook(output,count,length,width,source,destination,control):
        nonlocal calls
        if count>17:raise ValueError('Composed list capacity')
        args=dict(source_address=source,destination_address=destination,output_address=output)
        a=execute(old,0xcdb4,count,length,control,width,**args)
        b=execute(new,0x10203828,count,length,control,width,**args)
        if a!=b:raise ValueError('Composed descriptor difference')
        used=max(count,1)
        for index in range(used):
            last=index==used-1;offset=index*24
            # The caller's selected direction is fixed source, incrementing destination.
            wanted_source=source
            wanted_destination=(destination+index*4095*width)&0xffffffff
            word=lambda off:int.from_bytes(a[0][offset+off:offset+off+4],'little')
            if word(0)!=wanted_source or word(4)!=wanted_destination:raise ValueError('Composed descriptor addresses')
            if word(12)!=(control&~0x18000000 if last else control):raise ValueError('Composed descriptor control')
            if word(20)!=0xa5a5a5a5:raise ValueError('Composed untouched word')
        calls+=2
    result=configure(descriptor_hook=hook)
    return {'configuration':result,'descriptor_dependency':dependency,'decoded_descriptor_calls':calls,'source_admitted':False,'hardware_qualified':False,'limits':['Descriptor memory is isolated at the actual output address; configuration MMIO and descriptor writes not in one shared memory. Bus translation modeled in this run.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-configure-descriptors.json').write_text(json.dumps(result,indent=2)+'\n');print('Configuration descriptor calls:',result['decoded_descriptor_calls'])
