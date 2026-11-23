#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31ca28..0x31cb1e: create the BIG streams. Load the stream
 * parameters (322c94/322bac) from the pending request (*((uintptr_t)&em9305_ram_805c5c + 0x20u) + 4);
 * for each stream number i+1 below the request count (+20) that is listed
 * in the record's selection (count +202, list +203), allocate and set up
 * a stream from the request's access address, CRC, channel words and PHY,
 * keeping the first two allocated streams (+256/+260) with their index
 * (+268) and spacing (+269) and the first offset (+264 = +12 * i). A
 * stream number that is not listed gets a zero entry in the stream table
 * (+56, count +52). Then finish the request (31ccf4), start the BIG timer
 * (+208, +224 ms) and report status 0, or report 0x0d after 31cb40 when an
 * allocation fails. */
extern uint32_t opencfw_em9305_dispatch_child_322c94(uintptr_t record,
                                                     uintptr_t params);
extern void opencfw_em9305_dispatch_child_322bac(uintptr_t record,
                                                 uintptr_t parameters);
extern uintptr_t opencfw_em9305_radio_stream_allocate_316ad4(uintptr_t record);
extern uintptr_t opencfw_em9305_radio_stream_setup_327718(uintptr_t stream,
    uint32_t access,uint32_t crc,uint32_t lower,uint32_t upper,uint32_t phy);
extern uint32_t opencfw_em9305_dispatch_child_31ccf4(uintptr_t record,
                                                     uintptr_t params);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t timer,
                                                  uint32_t milliseconds);
extern uint32_t opencfw_em9305_dispatch_callback_31cb40(uintptr_t record);
extern uint32_t opencfw_em9305_dispatch_child_322e80(uintptr_t big,
                                                     uint32_t status);

uint32_t opencfw_em9305_dispatch_callback_31ca28(uintptr_t record)
{
    uintptr_t request=*(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x20u);
    (void)opencfw_em9305_dispatch_child_322c94(record,request+4u);
    opencfw_em9305_dispatch_child_322bac(record,request+4u);
    for(uint32_t index=0u;index<*(volatile uint8_t *)(request+20u);++index){
        uint32_t listed=*(volatile uint8_t *)(record+202u);
        uint32_t position=0u;
        if(listed!=0u){
            for(;;){
                if(position==listed)break;
                if(index+1u==*(volatile uint8_t *)(record+203u+position))break;
                ++position;
            }
            if(position!=listed){
                uintptr_t stream=opencfw_em9305_radio_stream_allocate_316ad4(record);
                if(stream==0u){
                    (void)opencfw_em9305_dispatch_callback_31cb40(record);
                    return opencfw_em9305_dispatch_child_322e80(record,0x0du);
                }
                (void)opencfw_em9305_radio_stream_setup_327718(stream,
                    *(volatile uint32_t *)(request+40u),
                    *(volatile uint16_t *)(request+50u),
                    *(volatile uint32_t *)(request+52u),
                    *(volatile uint32_t *)(request+56u),
                    *(volatile uint8_t *)(request+60u));
                if(*(volatile uint32_t *)(record+256u)==0u){
                    uint32_t period=*(volatile uint32_t *)(record+12u);
                    *(volatile uint32_t *)(record+256u)=stream;
                    *(volatile uint8_t *)(record+268u)=(uint8_t)index;
                    *(volatile uint32_t *)(record+264u)=period*index;
                }else if(*(volatile uint32_t *)(record+260u)==0u){
                    uint32_t first=*(volatile uint8_t *)(record+268u);
                    *(volatile uint32_t *)(record+260u)=stream;
                    *(volatile uint8_t *)(record+269u)=(uint8_t)(index-first);
                }
            }
        }
        if(position==*(volatile uint8_t *)(record+202u)){
            uint32_t slot=*(volatile uint8_t *)(record+52u);
            *(volatile uint8_t *)(record+52u)=(uint8_t)(slot+1u);
            *(volatile uint32_t *)(record+slot*4u+56u)=0u;
        }
    }
    (void)opencfw_em9305_dispatch_child_31ccf4(record,
                                               *(volatile uint32_t *)((uintptr_t)&em9305_ram_805c5c + 0x20u)+4u);
    (void)opencfw_em9305_wsf_timer_start_ms(record+208u,
                                            *(volatile uint32_t *)(record+224u));
    return opencfw_em9305_dispatch_child_322e80(record,0u);
}
