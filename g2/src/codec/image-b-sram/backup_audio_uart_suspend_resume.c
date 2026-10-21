/* SPDX-License-Identifier: MIT
 * Image-B UART audio suspend 0x1000ace8..0x1000ad0f and resume
 * 0x1000ad10..0x1000ad5f. Native source: binh_b_stage2.bin SHA256
 * d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_tx_abort_route_10004708(uint32_t port);
extern int32_t gx8002_image_b_uart_rx_abort_route_10004724(uint32_t port);
extern int32_t gx8002_image_b_uart_configure_1000451c(
    uint32_t port, uint32_t configuration);
extern int32_t gx8002_image_b_uart_rx_irq_enable_100046ac(
    uint32_t port, uint32_t callback, uint32_t context);
extern int32_t gx8002_image_b_audio_uart_rx_irq_1000b198(
    uint32_t port, uint32_t available);

int32_t gx8002_image_b_audio_uart_suspend_1000ace8(void)
{
    volatile uint32_t *base =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cc20);
    (void)gx8002_image_b_uart_tx_abort_route_10004708(base[8u / 4u]);
    (void)gx8002_image_b_uart_rx_abort_route_10004724(base[8u / 4u]);
    (void)gx8002_image_b_uart_tx_abort_route_10004708(base[0x184u / 4u]);
    (void)gx8002_image_b_uart_rx_abort_route_10004724(base[0x184u / 4u]);
    return 0;
}

int32_t gx8002_image_b_audio_uart_resume_1000ad10(void)
{
    volatile uint32_t *base =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002cc20);
    for (uint32_t index = 0u; index < 2u; ++index) {
        volatile uint32_t *state =
            (volatile uint32_t *)((uintptr_t)base + index * 0x17cu);
        if (state[0xcu / 4u] != 1u) continue;
        uint32_t port = state[8u / 4u];
        (void)gx8002_image_b_uart_tx_abort_route_10004708(port);
        port = state[8u / 4u];
        (void)gx8002_image_b_uart_rx_abort_route_10004724(port);
        port = state[8u / 4u];
        int32_t result = gx8002_image_b_uart_configure_1000451c(
            port, state[0x10u / 4u]);
        if (result != 0) return -1;
        (void)gx8002_image_b_uart_rx_irq_enable_100046ac(
            state[8u / 4u],
            (uint32_t)(uintptr_t)gx8002_image_b_audio_uart_rx_irq_1000b198,
            0u);
    }
    return 0;
}
