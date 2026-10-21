/* SPDX-License-Identifier: MIT
 * Main 0x4c3d9e: class 2 clock acquisition and pending timeout cleanup.
 */
#include <stdint.h>

extern uint32_t g2_main_clock_request_test_4c37a8(uint32_t, uint32_t);
extern uint32_t g2_main_clock_request_set_4c37fe(uint32_t, uint32_t,
                                                   uint32_t);
extern uint32_t g2_main_critical_save_473940(void);
extern uint32_t g2_main_clock_mode_read_480c56(uint8_t *);
extern uint64_t g2_main_clock_mode_set_4809c4(uint32_t, const uint32_t *,
                                               uint32_t, uint32_t);
extern uint64_t g2_main_clock_timeout_cleanup_4c3d70(uint32_t,
                                                       uint32_t, uint32_t,
                                                       uint32_t);

uint64_t g2_main_clock_acquire_2_4c3d9e(uint32_t id,
                                          uint32_t second,
                                          uint32_t third, uint32_t fourth)
{
    (void)third;
    (void)fourth;
    uint32_t result = 0u;
    uint32_t timeout = 0x96u;
    uint32_t mode_word = second;
    if (*(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001d0) == 0u)
        return ((uint64_t)mode_word << 32) | 7u;

    if (g2_main_clock_request_test_4c37a8(2u, (uint8_t)id) == 0u) {
        const uint32_t saved = g2_main_critical_save_473940();
        (void)g2_main_clock_mode_read_480c56((uint8_t *)&mode_word);
        volatile uint8_t *const active =
            (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f56);
        volatile uint32_t *const slot =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0x20074260);
        if (*active != 0u)
            timeout = *(const volatile uint32_t *)(uintptr_t)*slot;
        const uint8_t mode = (uint8_t)mode_word;
        const uint8_t selected =
            *(const volatile uint8_t *)(uintptr_t)UINT32_C(0x200001cc);
        if (mode == 0u) {
            if (selected == 1u) {
                mode_word = (mode_word & UINT32_C(0xffff0000)) | 0x100u;
                const uint32_t choice = 1u;
                (void)g2_main_clock_mode_set_4809c4(3u, &choice, 0u, 0u);
            } else {
                (void)g2_main_clock_mode_set_4809c4(2u, 0, 0u, 0u);
                if (*active == 0u)
                    *active = 1u;
            }
        } else if ((mode == 2u && selected == 0u) ||
                   (mode == 1u && selected == 1u)) {
            result = 3u;
        }
        if (result == 0u)
            (void)g2_main_clock_request_set_4c37fe(2u, (uint8_t)id, 1u);
        if (*active != 0u)
            *slot = (uint32_t)(uintptr_t)&timeout;
        __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
        (void)g2_main_clock_timeout_cleanup_4c3d70(
            (uint32_t)(uintptr_t)&timeout, 0u, 0u, 0u);
    } else {
        mode_word = g2_main_critical_save_473940();
        volatile uint8_t *const active =
            (volatile uint8_t *)(uintptr_t)UINT32_C(0x20074f56);
        volatile uint32_t *const slot =
            (volatile uint32_t *)(uintptr_t)UINT32_C(0x20074260);
        if (*active != 0u)
            timeout = *(const volatile uint32_t *)(uintptr_t)*slot;
        *slot = (uint32_t)(uintptr_t)&timeout;
        __asm__ volatile("msr primask, %0" :: "r"(mode_word) : "memory");
        (void)g2_main_clock_timeout_cleanup_4c3d70(
            (uint32_t)(uintptr_t)&timeout, 0u, 0u, 0u);
    }
    return ((uint64_t)mode_word << 32) | result;
}
