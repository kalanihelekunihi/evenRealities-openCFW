#include <stdint.h>
extern uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);
extern uint32_t opencfw_em9305_radio_record_request_30fc68(uintptr_t,uint32_t);
/* Native30425c..3042b0, preserving STB.AB old address and fresh slots. */
uint32_t opencfw_em9305_callback_30425c(uintptr_t owner,uint32_t first,
    uint32_t second,uintptr_t request,uint32_t selector)
{
    *(volatile uint8_t *)(uintptr_t)0x8015c4u=1u;
    uintptr_t base=0x8015ccu;
    uintptr_t record=*(volatile uint32_t *)(owner+44u);
    uint32_t replacement=*(volatile uint32_t *)(record+72u);
    uint32_t saved=*(volatile uint32_t *)(record+4u);
    *(volatile uint32_t *)(record+4u)=replacement;
    record=*(volatile uint32_t *)(owner+44u);
    (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
    record=*(volatile uint32_t *)(owner+44u);
    *(volatile uint32_t *)(base+8u)=first+second;
    *(volatile uint32_t *)(record+4u)=saved;
    (void)opencfw_em9305_common_radio_bind_30fc10(base);
    uint8_t frame[20];
    (void)opencfw_em9305_memset(frame,0u,20u);
    uint32_t prior=opencfw_em9305_radio_record_30fc28((uintptr_t)frame);
    (void)opencfw_em9305_radio_cancel_30fab8(prior);
    return opencfw_em9305_radio_record_request_30fc68(request,selector);
}
