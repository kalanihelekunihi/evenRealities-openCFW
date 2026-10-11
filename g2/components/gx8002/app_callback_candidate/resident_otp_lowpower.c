/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x100248cc. Direct native C-SKY instructions establish the
 * OTP-mode gate, analog register bit inserts, sync barriers, cache command,
 * and named doze instruction. This is a source candidate, not a hardware
 * execution claim.
 */
#include <stdint.h>

extern int32_t gx8002_resident_flash_otp_mode_25d04(uint32_t *mode);
extern void gx8002_resident_clock_switch_1m_25a14(void);

void gx8002_resident_otp_lowpower_enter_248cc(void)
{
    uint32_t mode = 0u;
    (void)gx8002_resident_flash_otp_mode_25d04(&mode);
    if (mode != UINT32_C(0x8002)) return;

    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0000000);
    uint32_t value = analog[0x24u / 4u];
    value = (value & ~((UINT32_C(1) << 8) | (UINT32_C(1) << 11) |
                       (UINT32_C(1) << 13) | (UINT32_C(15) << 14))) |
            (UINT32_C(1) << 11) | (UINT32_C(1) << 13) |
            (UINT32_C(1) << 14);
    analog[0x24u / 4u] = value;

    value = analog[0x28u / 4u];
    value = (value & ~((UINT32_C(1) << 8) | (UINT32_C(1) << 13) |
                       (UINT32_C(15) << 14))) |
            (UINT32_C(1) << 13) | (UINT32_C(1) << 14);
    analog[0x28u / 4u] = value;
    analog[0x38u / 4u] &= ~UINT32_C(1 << 4);
    analog[0x34u / 4u] = 15u;
    gx8002_resident_clock_switch_1m_25a14();
    __asm__ volatile("sync\n\tsync" ::: "memory");
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0xe000f004) = 5u;
    __asm__ volatile("sync\n\tsync" ::: "memory");
    analog[0] = 1u;
    __asm__ volatile("doze" ::: "memory");
}
