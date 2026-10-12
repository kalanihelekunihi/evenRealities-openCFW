/* SPDX-License-Identifier: MIT
 * Image-B UART configuration entry 0x1000451c..0x1000457d.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Clock snaps to a nearby 1 MHz boundary only within the native 100 Hz
 * tolerance; otherwise the unrounded frequency reaches the port record.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(
    uint32_t module, uint32_t enable);
extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t module);
extern int32_t gx8002_image_b_uart_apply_100043a4(volatile uint32_t *record);

int32_t gx8002_image_b_uart_configure_1000451c(
    uint32_t port, uint32_t configuration)
{
    if (port >= 2u) return -1;
    gx8002_image_b_platform_gate_10003be8(17u + (port != 0u), 1u);
    uint32_t frequency = gx8002_image_b_clock_frequency_10003cf0(16u);
    uint32_t remainder = frequency % UINT32_C(1000000);
    if (remainder <= 100u) {
        frequency -= remainder;
    } else if (UINT32_C(1000000) - remainder <= 100u) {
        frequency += UINT32_C(1000000);
        frequency -= remainder;
    }
    volatile uint32_t *record = (volatile uint32_t *)(uintptr_t)
        (UINT32_C(0x20016b84) + port * 128u);
    record[0xcu / 4u] = frequency;
    record[0x10u / 4u] = configuration;
    return gx8002_image_b_uart_apply_100043a4(record);
}
