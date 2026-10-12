#include <stdint.h>
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30fcd8(uintptr_t,uint32_t);
/* Authenticated native 3041e0..304210. Native 20-byte frame is entirely
 * cleared; owner+136 clear occurs before the actual fill (BL delay). */
uint32_t opencfw_em9305_callback_3041e0(uintptr_t owner)
{
    uint8_t frame[20];
    *(volatile uint8_t *)(uintptr_t)0x8015c4u=1u;
    *(volatile uint8_t *)(owner+136u)=0u;
    (void)opencfw_em9305_memset(frame,0u,20u);
    (void)opencfw_em9305_radio_record_30fc28((uintptr_t)frame);
    (void)opencfw_em9305_radio_request_30fcd8(owner+120u,1u);
    return 0u;
}
