#include <stdint.h>
extern uint32_t opencfw_em9305_auxiliary_ready_303f68(void);
extern uint32_t opencfw_em9305_radio_cancel_30fab8(uint32_t);
extern uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t);
/* Native3042b4..3042e6. Preserve native R0 including address returns. */
uint32_t opencfw_em9305_callback_3042b4(uint32_t incoming)
{
    uintptr_t current=opencfw_em9305_auxiliary_ready_303f68();
    uintptr_t record=*(volatile uint32_t *)(current+44u);
    uint32_t value=(uint32_t)record;
    uint32_t callback=*(volatile uint32_t *)(record+116u);
    if(callback==0u) {
        value=*(volatile uint8_t *)record;
        if(value!=15u)return value;
    }
    if(incoming==0u) {
        value=0x8015c4u;
        uint32_t flag=*(volatile uint8_t *)(uintptr_t)value;
        if(flag!=1u)return value;
        *(volatile uint8_t *)(uintptr_t)value=0u;
        value=opencfw_em9305_radio_cancel_30fab8(value);
    }
    return opencfw_em9305_common_radio_finish_3045c0(value);
}
