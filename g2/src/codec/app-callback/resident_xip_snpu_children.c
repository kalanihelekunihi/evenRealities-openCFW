/* SPDX-License-Identifier: MIT
 * Connected native SNPU bodies 0x102055a8/ac/b0, 0x102058d4,
 * 0x10205a90. The first two are authenticated single-instruction returns.
 */
#include <stdint.h>

extern void gx8002_resident_request_irq_2553c(uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_xip_npu_is_enabled_1020560c(uint32_t);
extern void gx8002_xip_npu_disable_10205600(uint32_t);
extern uint32_t gx8002_xip_npu_all_idle_102056e4(uint32_t);
extern void gx8002_resident_clock_snpu_enable_251ec(uint32_t);

static volatile uint32_t *const snpu_state =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);

void gx8002_xip_snpu_device_initialize_102055a8(uint32_t unused)
{
    (void)unused; /* native 0x102055a8: jmp r15 */
}

void gx8002_xip_snpu_device_exit_102055ac(void)
{
    /* native 0x102055ac: jmp r15 */
}

void gx8002_xip_snpu_request_irq_102055b0(uint32_t handler, uint32_t context)
{
    gx8002_resident_request_irq_2553c(12u, handler, context);
}

void gx8002_xip_snpu_tcb_initialize_102058d4(void)
{
    for (uint32_t group = 0u; group < 10u; ++group) {
        uintptr_t group_base = UINT32_C(0x20027350) + group * 0x90u;
        uint32_t next_address = (uint32_t)(group_base + 0x2cu);
        for (uint32_t index = 0u; index < 8u; ++index) {
            volatile uint32_t *entry = (volatile uint32_t *)(group_base +
                                                   index * 12u + 0x20u);
            entry[0] = UINT32_C(0x10080) | index;
            entry[1] = next_address & UINT32_C(0x07ffffff);
            next_address += 12u;
        }
        *(volatile uint32_t *)(group_base + 0x80u) = 0x10088u;
        *(volatile uint32_t *)(group_base + 0x10u) = UINT32_C(0x004100ff);
    }
}

int32_t gx8002_xip_snpu_suspend_10205a90(void)
{
    if (snpu_state[0x5c4u / 4u] == 0u) return -1;
    if (snpu_state[0] != 2u) {
        if (gx8002_xip_npu_is_enabled_1020560c(
                snpu_state[0x5c4u / 4u]) != 0u) {
            gx8002_xip_npu_disable_10205600(snpu_state[0x5c4u / 4u]);
            while (gx8002_xip_npu_all_idle_102056e4(
                       snpu_state[0x5c4u / 4u]) == 0u) {}
        }
        gx8002_resident_clock_snpu_enable_251ec(0u);
        snpu_state[0] = 2u;
    }
    return 0;
}
