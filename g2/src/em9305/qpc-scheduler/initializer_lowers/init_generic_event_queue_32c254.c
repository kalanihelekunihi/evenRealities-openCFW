#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32c254..0x32c2ae: drain the event queue at ((uintptr_t)&em9305_ram_8052d4 + 0x124u). For each
 * event build a 28-byte report (code 0x15 at +2, event byte +12 at +4,
 * event words +16/+20 at +8/+12 and +4/+8 at +16/+20); when the two word
 * pairs differ or the event bytes +0/+12 differ, bit 1 of the report byte
 * is set and the second pair is filled, otherwise it stays zero. The
 * report goes to the LL event callback and the event is released. Bytes
 * +5..+7 and +24..+26 are not written, as in stock; the queue handler id
 * lands at +27. */
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t out_u8);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);

uint32_t opencfw_em9305_init_callback_32c254(void)
{
    _Alignas(4) uint8_t report[28];
    for(;;){
        uintptr_t event=opencfw_em9305_wsf_event_remove(((uintptr_t)&em9305_ram_8052d4 + 0x124u),
                                                        (uintptr_t)&report[27]);
        if(event==0u)return 0u;
        *(uint32_t *)(void *)(report+20)=0u;
        *(uint32_t *)(void *)(report+16)=0u;
        uint32_t high=*(volatile uint32_t *)(event+20u);
        uint32_t low=*(volatile uint32_t *)(event+16u);
        *(uint32_t *)(void *)report=0x150000u;
        *(uint32_t *)(void *)(report+12)=high;
        uint32_t flags=*(volatile uint8_t *)(event+12u);
        *(uint32_t *)(void *)(report+8)=low;
        report[4]=(uint8_t)flags;
        uint32_t other_high=*(volatile uint32_t *)(event+8u);
        uint32_t other_low=*(volatile uint32_t *)(event+4u);
        if(((low^other_low)|(high^other_high))!=0u
           ||flags!=*(volatile uint8_t *)event){
            *(uint32_t *)(void *)(report+16)=other_low;
            *(uint32_t *)(void *)(report+20)=other_high;
            report[4]=(uint8_t)(flags|2u);
        }
        (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)report);
        (void)opencfw_em9305_wsf_event_release(event);
    }
}
