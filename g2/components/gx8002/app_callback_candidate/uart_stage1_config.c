/* SPDX-License-Identifier: MIT
 * UART boot stage-1 configuration at 0x10000c9c. The source configuration
 * pointer is a caller contract; native literal pools fix MMIO bases at
 * 0xa0005000 and 0xa0005080.
 */
#include <stdint.h>

extern void gx8002_uart_stage1_railcfg(void);
extern uint32_t gx8002_uart_stage1_time_ms(void);

int32_t gx8002_uart_stage1_uart_config(const uint32_t *config,
                                        uint32_t timeout_ms)
{
    if (config[0] == 0) return 0;
    volatile uint32_t *const uart =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    volatile uint32_t *const status =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005080);

    uart[0x3c / 4] &= ~UINT32_C(2);
    uart[0x3c / 4] &= ~UINT32_C(1);
    uart[0x1c / 4] = (uart[0x1c / 4] & ~UINT32_C(0x3f)) | config[4];
    uart[0x20 / 4] &= ~UINT32_C(0xff);
    uart[0x24 / 4] &= ~UINT32_C(0x1f);
    uart[0x20 / 4] |= config[5] & UINT32_C(0xff);
    uart[0x24 / 4] |= (config[5] & UINT32_C(0xfff)) >> 8;
    uart[0x28 / 4] = (uart[0x28 / 4] & ~UINT32_C(7)) | config[9];
    uart[0x2c / 4] = (uart[0x2c / 4] & ~UINT32_C(0x7f)) | config[6];
    uart[0x30 / 4] = (uart[0x30 / 4] & ~UINT32_C(7)) | (config[11] & 7u);
    uart[0x30 / 4] = (uart[0x30 / 4] & ~UINT32_C(0x30)) | (config[8] << 4);
    uart[0x3c / 4] = (uart[0x3c / 4] & ~UINT32_C(4)) | ((config[7] & 1u) << 2);
    uart[0x3c / 4] |= UINT32_C(2);
    uart[0x3c / 4] |= UINT32_C(1);

    gx8002_uart_stage1_railcfg();
    const uint32_t start = gx8002_uart_stage1_time_ms();
    while ((status[0x18 / 4] & 8u) == 0) {
        if (timeout_ms < gx8002_uart_stage1_time_ms() - start) return -1;
    }
    return 0;
}
