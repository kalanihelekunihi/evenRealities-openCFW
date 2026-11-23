#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x323c0c..0x323c76: compose a type-3 radio PDU for the record.
 * A 5-byte header (7, then zeros) is filled by children 318440 and
 * 3184f4 from the record's request block (+2516); the compose call is
 * forced to 9 when bit 11 of the controller options (*((uintptr_t)&em9305_ram_805a6c + 0x18u)) is set,
 * otherwise 1, with 0x50 allowed bits, no prefix and source +1696. */
extern uint32_t opencfw_em9305_child_318440(uintptr_t link,uintptr_t params,
                                            uintptr_t request);
extern void opencfw_em9305_child_3184f4(uintptr_t out,uintptr_t link,
                                        uintptr_t request);
extern uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t record,
    uint32_t forced,uint32_t allowed,uint32_t prefix,uintptr_t header,
    uintptr_t source,uintptr_t output,uint32_t type,uint32_t count);

uint32_t opencfw_em9305_child_323c0c(uintptr_t record,uintptr_t output,
                                     uint32_t count)
{
    _Alignas(4) uint8_t header[8];
    uintptr_t request=record+0x9d4u;
    uint32_t options=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805a6c + 0x18u);
    header[4]=0u;
    header[3]=0u;
    header[2]=0u;
    header[1]=0u;
    header[0]=7u;
    (void)opencfw_em9305_child_318440((uintptr_t)header,request,record);
    opencfw_em9305_child_3184f4((uintptr_t)header,request,record);
    uint32_t forced=(options&0x800u)!=0u?9u:1u;
    return opencfw_em9305_radio_compose_323dc0(record,forced,0x50u,0u,
        (uintptr_t)header,record+1696u,output,3u,count);
}
