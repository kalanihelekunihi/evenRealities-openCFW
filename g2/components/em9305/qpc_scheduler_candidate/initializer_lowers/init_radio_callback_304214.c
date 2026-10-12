#include <stdint.h>
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);
/* Authenticated 304214..30425a: exact cleared frame, R4 capture and
 * dynamic callback argument/return contract. Callback fields stay live. */
uint32_t opencfw_em9305_callback_304214(uintptr_t owner,uintptr_t record,
    uint32_t event,uint32_t unused_r3,uint32_t incoming_r4)
{
    (void)unused_r3;
    uint8_t frame[20];
    (void)opencfw_em9305_memset(frame,0u,20u);
    uint32_t prior=opencfw_em9305_radio_record_30fc28((uintptr_t)frame);
    (void)opencfw_em9305_radio_cancel_30fab8(prior);
    uint32_t status=1u;
    uint32_t value=*(volatile uint32_t *)(record+112u);
    if(value!=0u) {
        uintptr_t callback=*(volatile uint32_t *)(record+116u);
        if(callback!=0u) {
            (void)((uint32_t (*)(uintptr_t,uint32_t,uint32_t,uintptr_t,uint32_t))callback)
                (owner,incoming_r4,value,record+120u,2u);
            status=0u;
        }
    }
    uintptr_t final=*(volatile uint32_t *)(record+104u);
    (void)((uint32_t (*)(uintptr_t,uint32_t))final)(owner,event);
    return status;
}
