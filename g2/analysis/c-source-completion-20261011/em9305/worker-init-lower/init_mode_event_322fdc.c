#include <stdint.h>

/* Native 0x322fdc..0x323026. The two untouched event bytes are ambient
 * native stack contents; this provider intentionally does not initialize
 * them. A callback reading either byte remains an explicit ABI gate. */
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
uint32_t opencfw_em9305_mode_event_322fdc(uintptr_t context,
                                            uint32_t byte12)
{
    _Alignas(4) uint8_t local[20];
    volatile uint8_t *const record=local+4u;
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    int32_t index=(int32_t)((uint32_t)context-(uint32_t)base)/912;
    uint16_t short_index=(uint8_t)index;
    *(volatile uint8_t *)(local+8u)=(uint8_t)byte12;
    *(volatile uint8_t *)(local+7u)=(uint8_t)byte12;
    *(volatile uint16_t *)(void *)(local+16u)=0u;
    *(volatile uint32_t *)(void *)(local+12u)=0u;
    *(volatile uint8_t *)(local+6u)=7u;
    *(volatile uint16_t *)(void *)(local+10u)=short_index;
    *(volatile uint16_t *)(void *)(local+4u)=short_index;
    if (byte12==0u) {
        uint32_t pending=*(volatile uint32_t *)(context+676u);
        uint16_t counter=*(volatile uint16_t *)(context+680u);
        *(volatile uint32_t *)(void *)(local+12u)=pending;
        *(volatile uint16_t *)(void *)(local+16u)=counter;
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)record);
}
