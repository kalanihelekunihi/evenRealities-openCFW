/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern uint32_t open_cfw_gx8002_dma_bus_address(uint32_t);
/* Six-word stride; stock leaves word five untouched. The direction lookup
 * uses unsigned 16-bit entries, including 0xf001 for direction code one. */
void open_cfw_gx8002_dma_descriptors(volatile uint32_t *pattern,
                                    volatile uint32_t *output,
                                    int32_t count, int32_t length, uint8_t width)
{
    const uint16_t increments[4]={4095,0xf001,0,0};
    uint32_t control=pattern[3];
    uint32_t source_step=(uint32_t)increments[(control>>9)&3]*width;
    uint32_t destination_step=(uint32_t)increments[(control>>7)&3]*width;
    uint32_t source_offset=0,destination_offset=0;
    int32_t index=0;
    while (index<count-1) {
        output[0]=pattern[0]+source_offset;
        output[1]=pattern[1]+destination_offset;
        control=pattern[3];
        output[4]=4095;
        output[3]=control;
        output[2]=open_cfw_gx8002_dma_bus_address((uint32_t)(uintptr_t)(output+6));
        source_offset+=source_step;
        destination_offset+=destination_step;
        ++index;
        output+=6;
    }
    output[0]=pattern[0]+source_offset;
    output[1]=pattern[1]+destination_offset;
    output[3]=pattern[3]&~0x18000000u;
    int32_t remainder=length%4095;
    output[4]=remainder ? (uint32_t)remainder : 4095u;
    output[2]=0;
}
