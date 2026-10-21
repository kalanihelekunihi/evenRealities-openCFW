/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205254..0x102052d4. The rejected-context path
 * sets r4 to zero and performs the same low-address stores as stock code.
 * Their hardware outcome is a runtime precondition, not a success fallback.
 */
#include <stdint.h>

extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern uint32_t gx8002_xip_aout_select_hw_config_10205374(void);
extern uint32_t gx8002_xip_aout_handle_isr_102050cc(
    uint32_t, volatile uint8_t *);
extern void gx8002_resident_request_irq_2553c(
    uint32_t, uint32_t, uint32_t);

static volatile uint32_t *const aout =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00000);

uint32_t gx8002_xip_aout_alloc_playback_10205254(uint32_t mode)
{
    volatile uint8_t *const product_context =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x20026b94);
    uint32_t context_address;
    if (product_context[4] == 0u &&
        *(volatile uint32_t *)(void *)(product_context + 8u) == 0u &&
        (uint32_t)product_context[12] == mode) {
        gx8002_xip_memset_102099cc(
            (void *)(uintptr_t)UINT32_C(0x20026ba4), 0u, 36u);
        product_context[4] = 1u;
        context_address = UINT32_C(0x20026b94);
    } else {
        context_address = 0u;
    }

    *(volatile uint32_t *)(uintptr_t)(context_address + 0x14u) = 0u;
    *(volatile uint8_t *)(uintptr_t)(context_address + 0x18u) = (uint8_t)mode;
    uint32_t config_address = gx8002_xip_aout_select_hw_config_10205374();
    *(volatile uint32_t *)(uintptr_t)(context_address + 0x30u) = config_address;

    aout[0x0cu / 4u] = aout[0x0cu / 4u] | UINT32_C(0x00200000);
    aout[0u] = aout[0u] & UINT32_C(0x7fffffff);
    aout[0u] = (aout[0u] & ~UINT32_C(2)) |
               ((*(volatile uint32_t *)(uintptr_t)config_address << 1u) & 2u);
    aout[0u] = (aout[0u] & ~UINT32_C(1)) |
               (*(volatile uint32_t *)(uintptr_t)(config_address + 4u) & 1u);
    aout[4u / 4u] = aout[4u / 4u] & ~UINT32_C(0x100);
    gx8002_resident_request_irq_2553c(
        13u, (uint32_t)(uintptr_t)&gx8002_xip_aout_handle_isr_102050cc,
        context_address);
    return context_address;
}
