/* SPDX-License-Identifier: MIT
 * Native XIP 0x10207808..0x10207895 and SNPU state leaf 0x10205e28.
 * Pinned NationalChip lvp/common/lvp_pmu.c owns the control algorithm;
 * direct disassembly authenticates SRAM handle 0x2002dfbc, callback
 * layout, ordered PMU calls, wakeup target 0x10023500 and exact log.
 */
#include <stdint.h>

extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t);
extern void gx8002_xip_audio_suspend_10207644(void);
extern void gx8002_xip_snpu_exit_10205d40(void);
extern uint32_t gx8002_resident_platform_config_25d74(uint32_t, uint32_t *);
extern void gx8002_resident_irq_save_disable_wrapper_25534(void);
extern uint32_t gx8002_xip_audio_set_interrupt_enable_102047b8(
    uint32_t, uint32_t);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern void gx8002_resident_otp_lowpower_enter_248cc(void);

uint32_t gx8002_xip_snpu_get_state_10205e28(void)
{
    return *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20027350);
}

int32_t gx8002_xip_tws_command_10207808(uint32_t wakeup_mode)
{
    volatile uint32_t *const handle =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002dfbc);
    uint32_t irq_state = g2_codec_critical_save();
    if (handle[0] != 0u) {
        g2_codec_critical_restore(irq_state);
        return -1;
    }
    for (uint32_t index = 0u; index < handle[2]; ++index) {
        uintptr_t callback_address = (uintptr_t)handle[4u + index * 2u];
        void *private_data = (void *)(uintptr_t)handle[5u + index * 2u];
        int32_t (*callback)(void *) =
            (int32_t (*)(void *))callback_address;
        (void)callback(private_data);
    }
    g2_codec_critical_restore(irq_state);
    gx8002_xip_audio_suspend_10207644();
    while (gx8002_xip_snpu_get_state_10205e28() == 1u) {}
    gx8002_xip_snpu_exit_10205d40();
    uint32_t wakeup[2];
    ((uint8_t *)wakeup)[0] = 1u;
    wakeup[1] = UINT32_C(0x10023500);
    (void)gx8002_resident_platform_config_25d74(3u, &wakeup_mode);
    (void)gx8002_resident_platform_config_25d74(5u, wakeup);
    gx8002_resident_irq_save_disable_wrapper_25534();
    if ((wakeup_mode & 4u) != 0u)
        (void)gx8002_xip_audio_set_interrupt_enable_102047b8(0x10000u, 1u);
    (void)gx8002_xip_tws_publish_10206c24("set mcu sleep\n");
    gx8002_resident_otp_lowpower_enter_248cc();
    return 0;
}
