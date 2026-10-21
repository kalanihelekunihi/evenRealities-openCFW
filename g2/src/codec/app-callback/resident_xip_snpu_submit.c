/* SPDX-License-Identifier: MIT
 * Native XIP 0x10205a00..0x10205a89. Direct disassembly gives state
 * split, 28-bit physical command pointer, 0x20000000 mapped window,
 * cache/command ordering, and active slot at 0x20027350+0x5c0.
 */
#include <stdint.h>

extern void gx8002_xip_npu_get_over_command_10205860(uint32_t, uint32_t *);
extern void gx8002_xip_npu_set_task_head_10205898(uint32_t, uint32_t);
extern void gx8002_xip_snpu_task_cache_flush_102059e8(uint32_t *);
extern void gx8002_xip_npu_enable_102055f4(uint32_t);
extern void g2_codec_header_sync(void *, uint32_t);

void gx8002_xip_snpu_submit_task_10205a00(uint32_t *task)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    uint32_t task_cmd = ((uint32_t)(uintptr_t)task + 16u) & 0x0fffffffu;
    uint32_t previous = control[0x170u];
    if (previous == 0u) {
        control[0] = 1u;
    } else if (control[0] == 2u) {
        uint32_t over_address = 0u;
        gx8002_xip_npu_get_over_command_10205860(
            control[0x171u], &over_address);
        if (over_address != 0u) {
            *(volatile uint32_t *)(uintptr_t)(previous + 4u) = task_cmd;
            task_cmd = *(volatile uint32_t *)(uintptr_t)(
                over_address + UINT32_C(0x20000004));
        }
        control[0] = 1u;
    } else {
        gx8002_xip_snpu_task_cache_flush_102059e8(task);
        *(volatile uint32_t *)(uintptr_t)(previous + 4u) = task_cmd;
        g2_codec_header_sync((void *)(uintptr_t)previous, 8u);
        control[0x170u] = (uint32_t)(uintptr_t)task;
        return;
    }
    gx8002_xip_npu_set_task_head_10205898(control[0x171u], task_cmd);
    gx8002_xip_snpu_task_cache_flush_102059e8(task);
    gx8002_xip_npu_enable_102055f4(control[0x171u]);
    control[0x170u] = (uint32_t)(uintptr_t)task;
}
