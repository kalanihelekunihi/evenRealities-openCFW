# SPDX-License-Identifier: MIT
import json,subprocess
import verify_gx8002_dcache_clean_range as cache
from itertools import product
from verify_gx8002_uart_transmit_dma import verify as setup_verify,execute as setup,ROOT,decode
from verify_gx8002_dma_transfer import verify as transfer_verify,execute as transfer
from verify_gx8002_dma_configure import verify as config_verify,execute as configure
from verify_gx8002_dma_bus_address import verify as bus_verify,execute as bus
from verify_gx8002_dma_descriptors import verify as descriptors_verify,execute as descriptors
from verify_gx8002_dma_clear import verify as clear_verify,execute as clear


def verify():
    dependencies=[setup_verify(),transfer_verify(),config_verify(),bus_verify(),descriptors_verify(),clear_verify(),cache.verify()]
    old_cache,new_cache=cache.programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc694','--stop-address=0xd200',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new={}
    for folder,file in [('uart-transmit-dma','dma'),('dma-transfer','transfer'),('dma-configure','configure'),('dma-bus-address','bus_address'),('dma-descriptors','descriptors'),('dma-clear','clear')]:new.update(decode((ROOT/f'build/gx8002-{folder}/{file}.disassembly.txt').read_text()))
    cases=0;bus_calls=0;descriptor_calls=0;clear_calls=0;cache_calls=0
    for port,channel,length in product((0,1),(0,1),(0,1,4095,4096,69615,69616,0xffffffff)):
        def run(code,source):
            configs=[];translations=[];lists=[];clears=[];caches=[]
            def cache_hook(address,size):
                if (address,size)!=(0x20060000,416) or len(lists)!=1:raise ValueError("Descriptor cache input/order")
                result=cache.execute(new_cache if source else old_cache,cache.ADDRESS if source else cache.OFFSET,address,size,0x12345678)
                if result!=(cache.expected(address,size),True):raise ValueError("Descriptor cache commands")
                caches.append(result)
            def clear_hook(number):
                if number!=channel:raise ValueError("DMA clear channel forwarding")
                result=clear(code,0x10203804 if source else 0xcd90,number,0xa1000000)
                expected=[("read",0x2002e93c,0xa1000000)]+[("write",0xa1000000+offset,1<<channel) for offset in (0x338,0x340,0x348,0x350,0x358)]
                if result!=expected:raise ValueError("DMA clear ordered registers")
                if translations or lists:raise ValueError("DMA clear must precede address and list setup")
                clears.append(result)
            def bus_hook(address):
                value=bus(code,0x10203c60 if source else 0xd1ec,address)
                wanted=address%0x10000000 if 0x10000000<=address<0x30000000 else address
                if value!=wanted:raise ValueError("Nested bus translation")
                translations.append((address,value));return value
            def descriptor_hook(output,count,length,width,src,dst,control):
                result=descriptors(code,0x10203828 if source else 0xcdb4,count,length,control,width,
                    source_address=src,destination_address=dst,output_address=output,
                    bus_hook=lambda address:bus(code,0x10203c60 if source else 0xd1ec,address))
                data=result[0];used=max(count,1)
                signed_length=length if length<0x80000000 else length-0x100000000
                remainder=signed_length-(abs(signed_length)//4095*(-1 if signed_length<0 else 1))*4095
                for index in range(used):
                    last=index==used-1
                    words=[int.from_bytes(data[index*24+off:index*24+off+4],'little') for off in range(0,24,4)]
                    expected=[(src+index*4095*width)&0xffffffff,dst,
                        0 if last else (output+(index+1)*24)%0x10000000,
                        control&~0x18000000 if last else control,
                        ((remainder or 4095)&0xffffffff) if last else 4095,0xa5a5a5a5]
                    if words!=expected:raise ValueError('UART descriptor contents')
                if data[used*24:]!=bytes([0xa5])*(432-used*24):raise ValueError('UART descriptor bounds')
                lists.append(result)
            def transfer_hook(dst,src,size,number,pointer,fields):
                def config_hook(a,b,n,c,p):
                    if (a,b,n,c,p)!=(dst,src,size,number,pointer):raise ValueError('Configuration forwarding')
                    result=configure(code,0x102038f4 if source else 0xce80,fields,n,c,destination=a,source=b,bus_hook=bus_hook,descriptor_hook=descriptor_hook,clear_hook=clear_hook)
                    configs.append(result);return result[0]
                return transfer(code,0x10203b78 if source else 0xd104,dst,src,size,number,pointer,0,0xa1000000,configure_hook=config_hook,cache_hook=cache_hook,descriptor_address=0x20060000)[0]
            result=setup(code,0x10203108 if source else 0xc694,port,0x20050000,length,channel,3,4,0xffffffff,transfer_hook=transfer_hook)
            return result,configs,translations,lists,clears,caches
        a=run(old,False);b=run(new,True)
        if a!=b or len(a[1])!=1 or a[0][0]!=0:raise ValueError('Nested setup/transfer/configure mismatch')
        signed=length if length<0x80000000 else length-0x100000000
        quotient=abs(signed)//4095*(-1 if signed<0 else 1);count=(quotient+int(signed!=quotient*4095))&0xffffffff
        if a[1][0][0]!=(0xffffffff if (count*24)&0xffffffff>416 else 0):raise ValueError('Configuration capacity result')
        expected=[(0x20050000,0x50000),(0xa0000000,0xa0000000)]
        if a[1][0][0]==0:expected.append((0x20060000,0x60000))
        if a[2]!=expected:raise ValueError("DMA bus argument order")
        if len(a[3])!=int(a[1][0][0]==0):raise ValueError("Descriptor capacity gate")
        if len(a[4])!=1:raise ValueError("DMA clear invocation count")
        if len(a[5])!=len(a[3]):raise ValueError("Descriptor cache capacity gate")
        cache_calls+=len(a[5]);clear_calls+=len(a[4]);descriptor_calls+=len(a[3]);bus_calls+=len(a[2]);cases+=1
    return {'dependencies':dependencies,'decoded_cases':cases,'decoded_bus_calls':bus_calls,'decoded_descriptor_calls':descriptor_calls,'decoded_clear_calls':clear_calls,'decoded_cache_calls':cache_calls,'source_admitted':False,'hardware_qualified':False,'limits':['Setup, transfer and configure decoded in separate frames; bus translation decoded; descriptor builder and its bus calls decoded; configure clear decoded; transfer cache decoded at the same descriptor-list address; descriptor memory isolated. Stack config content forwarded explicitly. No physical DMA or firmware completion claim.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-configure.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
