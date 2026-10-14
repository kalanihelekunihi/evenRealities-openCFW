/* SPDX-License-Identifier: MIT
 * Main 0x539a40 queue configuration and 0x44b0b6 pin mode update.
 */
#include <stdint.h>

extern uint32_t g2_main_critical_save_473940(void);

uint64_t g2_main_queue_pin_mode_44b0b6(uint32_t mode,
                                        uint32_t unused1,
                                        uint32_t unused2,
                                        uint32_t high)
{
    (void)unused1;
    (void)unused2;
    const uint32_t saved = g2_main_critical_save_473940();
    volatile uint32_t *const pin =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40008858);
    *pin = (*pin & UINT32_C(0xffffffbf)) | ((mode & 1u) << 6);
    __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
    return ((uint64_t)high << 32) | saved;
}

uint32_t g2_main_queue_config_539a40(uint32_t queue,
                                      const void *configuration)
{
    if (queue == 0u ||
        (*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x01ffffff)) != UINT32_C(0x01504c30))
        return 2u;
    if ((*(const volatile uint32_t *)(uintptr_t)queue &
         UINT32_C(0x02000000)) != 0u)
        return 7u;

    const uint8_t *const cfg = (const uint8_t *)configuration;
    if (cfg[3] >= 0x40u) return 6u;
    const uint16_t count = (uint16_t)cfg[6] | ((uint16_t)cfg[7] << 8);
    if (cfg[2] == 1u) {
        if ((uint16_t)(count - 4u) > 0x3bcu) return 6u;
    } else if ((uint16_t)(count - 10u) > 0x56u) {
        return 6u;
    }
    if (cfg[4] >= 8u || cfg[5] >= 8u || cfg[5] > cfg[4])
        return 6u;

    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204d8);
    volatile uint32_t *const data =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204dc);
    volatile uint32_t *const timing =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x400204e0);
    *control = (*control & UINT32_C(0xfffffdff)) |
               ((uint32_t)(cfg[1] & 1u) << 9);
    *control = (*control & UINT32_C(0xffffffdf)) |
               ((uint32_t)(cfg[0] & 1u) << 5);
    *control = (*control & UINT32_C(0xfffffff7)) |
               ((uint32_t)(cfg[2] & 1u) << 3);
    const uint32_t payload = (uint32_t)cfg[8] | ((uint32_t)cfg[9] << 8) |
                             ((uint32_t)cfg[10] << 16) |
                             ((uint32_t)cfg[11] << 24);
    *data = (payload & UINT32_C(0x00ffffff)) |
            (*data & UINT32_C(0xff000000));
    *timing = (*timing & UINT32_C(0xf000ffff)) |
              ((uint32_t)(count & 0xfffu) << 16);
    *timing = ((uint32_t)cfg[3] & 0x3fu) |
              (*timing & UINT32_C(0xffffffc0));
    *timing = (*timing & UINT32_C(0xffff8fff)) |
              ((uint32_t)(cfg[4] & 7u) << 12);
    *timing = (*timing & UINT32_C(0xfffff8ff)) |
              ((uint32_t)(cfg[5] & 7u) << 8);
    (void)g2_main_queue_pin_mode_44b0b6(cfg[0], 0u, 0u, 0u);
    *control &= UINT32_C(0xffffffef);
    *control |= 1u;
    *control &= UINT32_C(0xfffffffd);
    *control &= UINT32_C(0xfffffffb);
    return 0u;
}
