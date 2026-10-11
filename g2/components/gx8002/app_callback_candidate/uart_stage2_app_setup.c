/* SPDX-License-Identifier: MIT
 * UART stage-2 application setup at native 0x1000547c.
 * Lower calls remain separately identified by their native entry points.
 */
#include <stdint.h>

extern void gx8002_uart_stage2_reset_state_29d4(void);
extern uint32_t gx8002_uart_stage2_default_baud_2a1c(void);
extern void gx8002_uart_stage2_set_baud_2a50(uint32_t port, uint32_t baud);
extern void gx8002_uart_stage2_setup_5434(void);
extern void gx8002_uart_stage2_configure_61e4(uint32_t first, uint32_t second);
extern void gx8002_uart_stage2_vic_restore_30b4(void);
extern void gx8002_uart_stage2_setup_4db0(void);
extern void gx8002_uart_stage2_setup_4388(void);

void gx8002_uart_stage2_application_setup_547c(void)
{
    gx8002_uart_stage2_reset_state_29d4();
    volatile uint32_t *const config =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20009084);
    const uint32_t port = config[0];
    if (port != 0) {
        gx8002_uart_stage2_set_baud_2a50(0, UINT32_C(0x1c200));
    } else {
        const uint32_t mode = config[1];
        const uint32_t baud = gx8002_uart_stage2_default_baud_2a1c();
        gx8002_uart_stage2_set_baud_2a50(mode == 1u ? mode : 0u, baud);
    }
    gx8002_uart_stage2_setup_5434();
    gx8002_uart_stage2_configure_61e4(UINT32_C(0x2000e800),
                                         UINT32_C(0x00021800));
    gx8002_uart_stage2_vic_restore_30b4();
    gx8002_uart_stage2_setup_4db0();
    gx8002_uart_stage2_setup_4388();
}

extern int32_t gx8002_uart_stage2_report_lower_5b28(const char *message,
                                                      uint32_t mode);
extern void gx8002_uart_stage2_prepare_lower_5bf8(void);
extern void gx8002_uart_stage2_prepare_lower_618c(const void *literal);
extern int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...);

int32_t gx8002_uart_stage2_report_5c64(const char *message, uint32_t mode)
{
    return gx8002_uart_stage2_report_lower_5b28(message, mode);
}

void gx8002_uart_stage2_prepare_5c6c(void)
{
    gx8002_uart_stage2_prepare_lower_5bf8();
}

void gx8002_uart_stage2_prepare_5c74(void)
{
    gx8002_uart_stage2_prepare_lower_618c(
        (const void *)(uintptr_t)UINT32_C(0x100085a4));
}

void gx8002_uart_stage2_application_main_5a4c(void)
{
    if (*(const volatile uint8_t *)(uintptr_t)UINT32_C(0x20002005) == 3u)
        gx8002_uart_stage2_report_5c64(
            (const void *)(uintptr_t)UINT32_C(0x10008508), 0);
    gx8002_uart_stage2_prepare_5c74();
    gx8002_uart_stage2_prepare_5c6c();
    (void)gx8002_uart_stage2_launch_61a4(
        (const char *)(uintptr_t)UINT32_C(0x10008518));
}
