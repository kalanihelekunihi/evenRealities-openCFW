/* SPDX-License-Identifier: MIT. Stock43048e bounded initializer retry. */
#include "context_claim.h"
extern uint32_t opencfw_bl_power_register_update(uint32_t,uint32_t);
extern void opencfw_boot_delay_scaled(uint32_t);
#define WORD(p) (*(volatile uint32_t *)(uintptr_t)(p))
uint32_t opencfw_boot_context_retry(uint32_t index)
{
    if ((uint8_t)index==4u) {
        uint32_t config=WORD(0x20000374u+((uint8_t)index<<4)+8u);
        (void)opencfw_bl_power_register_update(WORD(config),WORD(0x434158u));
        config=WORD(0x20000374u+((uint8_t)index<<4)+8u);
        (void)opencfw_bl_power_register_update(WORD(config+4u),WORD(0x434158u));
    }
    uint32_t status=0u;
    for (uint32_t tries=0;tries<1000u;++tries) {
        struct opencfw_iom_context *h=(struct opencfw_iom_context *)(uintptr_t)
            WORD(0x20000374u+((uint8_t)index<<4)+4u);
        status=opencfw_boot_context_transaction(h,2u,1u);
        if (!status) break;
        opencfw_boot_delay_scaled(10u);
    }
    return status?4u:0u;
}
