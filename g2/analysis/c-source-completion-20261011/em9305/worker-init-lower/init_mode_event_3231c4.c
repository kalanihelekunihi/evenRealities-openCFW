#include <stdint.h>

/* Native 0x3231c4..0x323228. The native stack record has ambient bytes
 * +5 and +9..+11; the ten-byte copy can expose +5 and +9. They are left
 * untouched here, and callback/copy equality remains gated on that ambient
 * stack provenance. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
uint32_t opencfw_em9305_mode_event_3231c4(uintptr_t context)
{
    uint32_t code=*(volatile uint8_t *)(context+12u);
    if (code==255u) return (uint32_t)context;
    _Alignas(4) uint8_t record[12];
    uint32_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    int32_t index=(int32_t)((uint32_t)context-base)/912;
    uint32_t flags=*(volatile uint8_t *)(context+636u);
    *(volatile uint8_t *)(record+8u)=(uint8_t)code;
    *(volatile uint8_t *)(record+4u)=0u;
    *(volatile uint16_t *)(void *)(record+2u)=6u;
    *(volatile uint16_t *)(void *)(record+6u)=(uint8_t)index;
    *(volatile uint16_t *)(void *)record=(uint8_t)index;
    if ((flags&1u)!=0u) *(volatile uint8_t *)(record+8u)=22u;
    uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8028c4u;
    if (callback!=0u) {
        uint32_t accepted=((uint32_t (*)(uint32_t,uintptr_t))callback)(
            (uint8_t)index,callback);
        if (accepted!=0u) {
            uintptr_t destination=context+800u;
            uint32_t result=(uint32_t)(uintptr_t)opencfw_em9305_memcpy(
                (void *)destination,record,10u);
            *(volatile uint8_t *)(destination-2u)=1u;
            return result;
        }
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)record);
}
