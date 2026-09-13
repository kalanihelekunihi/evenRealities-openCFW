# SPDX-License-Identifier: MIT
"""Execute source-linked UART DMA submission with checked nested helper effects."""
from verify_gx8002_dma_transfer import execute as transfer
from execute_gx8002_dma_configure import execute as configure
from execute_gx8002_dma_descriptors import execute as descriptors
from verify_gx8002_dma_bus_address import execute as bus
from verify_gx8002_dma_clear import execute as clear
from verify_gx8002_dcache_clean_range import execute as clean,expected as expected_clean


def execute(code,symbols,destination,source,length,channel,pointer,fields):
    def symbol(name):return symbols['open_cfw_gx8002_'+name]
    state=symbol('dma_state');base=0xa1000000
    output=(state+(23 if channel==0 else 455))&~15
    translations=[];lists=[];clears=[];caches=[];configs=[]
    def bus_hook(address):
        result=bus(code,symbol('dma_bus_address'),address)
        wanted=address%0x10000000 if 0x10000000<=address<0x30000000 else address
        if result!=wanted:raise ValueError('Linked transfer bus translation')
        translations.append((address,result));return result
    def clear_hook(number):
        if number!=channel or translations or lists:raise ValueError('Linked transfer clear order')
        actual=clear(code,symbol('dma_clear'),number,base,state_address=state)
        wanted=[('read',state,base)]+[('write',base+off,1<<number) for off in (0x338,0x340,0x348,0x350,0x358)]
        if actual!=wanted:raise ValueError('Linked transfer clear effects')
        clears.append(actual)
    def descriptor_hook(address,count,size,width,src,dst,control):
        if address!=output:raise ValueError('Linked transfer descriptor storage')
        result=descriptors(code,symbol('dma_descriptors'),count,size,control,width,
            source_address=src,destination_address=dst,output_address=address,
            bus_hook=bus_hook,bus_address=symbol('dma_bus_address'))
        data=result[0];used=max(count,1)
        signed=size if size<0x80000000 else size-0x100000000
        remainder=signed-(abs(signed)//4095*(-1 if signed<0 else 1))*4095
        for index in range(used):
            last=index==used-1
            words=[int.from_bytes(data[index*24+off:index*24+off+4],'little') for off in range(0,24,4)]
            wanted=[(src+index*4095*width)&0xffffffff,dst,
                0 if last else (output+(index+1)*24)%0x10000000,
                control&~0x18000000 if last else control,
                ((remainder or 4095)&0xffffffff) if last else 4095,0xa5a5a5a5]
            if words!=wanted:raise ValueError('Linked UART descriptor contents')
        if data[used*24:]!=bytes([0xa5])*(432-used*24):raise ValueError('Linked UART descriptor bounds')
        lists.append(result)
    def config_hook(dst,src,size,number,config):
        if (dst,src,size,number,config)!=(destination,source,length,channel,pointer):raise ValueError('Linked configuration handoff')
        helpers={symbol('dma_clear'):0x10203804,symbol('dma_bus_address'):0x10203c60,symbol('dma_descriptors'):0x10203828}
        result=configure(code,symbol('dma_configure'),fields,size,number,
            destination=dst,source=src,state_address=state,descriptor_address=output,
            helper_addresses=helpers,clear_hook=clear_hook,bus_hook=bus_hook,descriptor_hook=descriptor_hook)
        configs.append(result);return result[0]
    def cache_hook(address,size):
        if (address,size)!=(output,416) or len(lists)!=1:raise ValueError('Linked descriptor cache ordering')
        actual=clean(code,symbol('dcache_clean_range'),address,size,0x12345678)
        if actual!=(expected_clean(address,size),True):raise ValueError('Linked descriptor cache effects')
        caches.append(actual)
    helpers={symbol('dma_configure'):0x102038f4,symbol('dcache_clean_range'):0x10025664}
    result,trace,memory=transfer(code,symbol('dma_transfer'),destination,source,length,channel,pointer,0,base,
        configure_hook=config_hook,cache_hook=cache_hook,descriptor_address=output,state_address=state,helper_addresses=helpers)
    signed=length if length<0x80000000 else length-0x100000000
    quotient=abs(signed)//4095*(-1 if signed<0 else 1)
    count=(quotient+int(signed!=quotient*4095))&0xffffffff
    accepted=((count*24)&0xffffffff)<=416
    if result!=(0 if accepted else 0xffffffff) or len(configs)!=1 or len(clears)!=1:raise ValueError('Linked transfer capacity result')
    if len(lists)!=int(accepted) or len(caches)!=int(accepted):raise ValueError('Linked transfer capacity effects')
    events=[event for event in trace if event[0]=='cache' or event[0]=='write' and event[1]>=base]
    wanted=[] if not accepted else [('write',base+0x310,257<<channel),('cache',output,416),('write',base+0x3a0,257<<channel)]
    if events!=wanted:raise ValueError('Linked descriptor publication ordering')
    return result,{'transfers':1,'configurations':len(configs),'descriptors':len(lists),'clears':len(clears),'caches':len(caches),'translations':len(translations)}
