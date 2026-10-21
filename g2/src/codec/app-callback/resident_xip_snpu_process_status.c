/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10205bd8 SNPU interrupt status dispatcher.
 * The queue layout matches selected 0x10205d60 task construction;
 * overtime reset remains an explicit native child contract.
 */
#include <stdint.h>

extern void gx8002_xip_npu_get_interrupt_102056f0(uint32_t, uint32_t *);
extern void gx8002_xip_npu_clear_without_overflow_102057e0(uint32_t, uint32_t);
extern void gx8002_xip_npu_clear_overflow_10205838(uint32_t, uint32_t);
extern void gx8002_xip_npu_get_over_command_10205860(uint32_t, uint32_t *);
extern void gx8002_xip_npu_get_overflow_command_10205870(uint32_t, uint32_t *);
extern int32_t gx8002_xip_snpu_suspend_10205a90(void);
extern void gx8002_xip_snpu_overtime_reset_10205b1c(void);

typedef void (*snpu_callback3)(uint32_t, uint32_t, uint32_t);
typedef void (*snpu_callback2)(uint32_t, uint32_t);

int32_t gx8002_xip_snpu_process_status_10205bd8(void)
{
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
    uint32_t npu = state[0x171u];
    uint32_t status = 0u;
    gx8002_xip_npu_get_interrupt_102056f0(npu, &status);
    gx8002_xip_npu_clear_without_overflow_102057e0(npu, status);

    if ((status & 1u) != 0u) {
        uint32_t over_command = 0u;
        gx8002_xip_npu_get_over_command_10205860(npu, &over_command);
        if (state[0x174u] != over_command) {
            state[0x174u] = over_command;
            uint32_t event = 1u;
            uint32_t end = state[0x16du];
            uint32_t current = state[0x16cu];
            for (;;) {
                uint32_t callback = state[(current + 1u) * 0x24u];
                uint32_t task_word = state[current * 0x24u + 0x25u];
                uint32_t userdata = state[current * 0x24u + 0x26u];
                uint32_t next = (current + 1u) % 10u;
                if (end == next) {
                    event = 2u;
                    (void)gx8002_xip_snpu_suspend_10205a90();
                }
                if ((uint32_t)(uintptr_t)(state + current * 0x24u + 4u) ==
                    over_command + UINT32_C(0x20000000)) {
                    state[0] = event;
                    state[0x16cu] = next;
                    if (callback != 0u)
                        ((snpu_callback2)(uintptr_t)(callback & ~1u))(
                            task_word, event);
                    break;
                }
                current = next;
                if (callback != 0u)
                    ((snpu_callback3)(uintptr_t)(callback & ~1u))(
                        task_word, event, userdata);
            }
        }
        return 0;
    }

    if ((status & (8u | 4u)) != 0u) {
        gx8002_xip_snpu_overtime_reset_10205b1c();
    } else if ((status & 0x20u) != 0u) {
        uint32_t overflow_command;
        gx8002_xip_npu_get_overflow_command_10205870(
            npu, &overflow_command);
        gx8002_xip_npu_clear_overflow_10205838(npu, status);
    } else {
        return (int32_t)((uint8_t)~((status & 0x40u) != 0u)) + 1;
    }
    return 0;
}
