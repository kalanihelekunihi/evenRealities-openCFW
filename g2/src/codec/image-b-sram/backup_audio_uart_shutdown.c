/* SPDX-License-Identifier: MIT
 * Image-B dual-port UART audio shutdown 0x1000b6f0..0x1000b73f.
 * Native source: binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * The 448/20/760-byte clear extents and abort order are native operands.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_uart_tx_abort_route_10004708(uint32_t port);
extern int32_t gx8002_image_b_uart_rx_abort_route_10004724(uint32_t port);
extern void gx8002_image_b_zero_100113c4(
    void *destination, uint32_t value, uint32_t bytes);

int32_t gx8002_image_b_audio_uart_shutdown_1000b6f0(void)
{
    volatile uint8_t *base = (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002cc20);
    uint32_t port = *(volatile uint32_t *)(volatile void *)(base + 8u);
    (void)gx8002_image_b_uart_tx_abort_route_10004708(port);
    port = *(volatile uint32_t *)(volatile void *)(base + 8u);
    (void)gx8002_image_b_uart_rx_abort_route_10004724(port);
    port = *(volatile uint32_t *)(volatile void *)(base + 0x184u);
    *(volatile uint32_t *)(volatile void *)(base + 0xcu) = 0u;
    (void)gx8002_image_b_uart_tx_abort_route_10004708(port);
    port = *(volatile uint32_t *)(volatile void *)(base + 0x184u);
    (void)gx8002_image_b_uart_rx_abort_route_10004724(port);
    *(volatile uint32_t *)(volatile void *)(base + 0x188u) = 0u;
    gx8002_image_b_zero_100113c4((void *)(base + 0x310u), 0u, 448u);
    gx8002_image_b_zero_100113c4(
        (void *)(uintptr_t)UINT32_C(0x2002d770), 0u, 20u);
    gx8002_image_b_zero_100113c4((void *)base, 0u, 760u);
    return 0;
}
