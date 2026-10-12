/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x1020854c UART async teardown. Three SRAM clear
 * bases resolve from stock literal-pool words at 0x10208598..0x102085a0.
 */
#include <stdint.h>

extern volatile uint32_t *gx8002_xip_uart_channel_lookup_10207ac0(uint32_t);
extern uint32_t gx8002_xip_uart_transmit_abort_102036e8(uint32_t);
extern uint32_t gx8002_xip_uart_receive_abort_10203704(uint32_t);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);

uint32_t gx8002_xip_uart_async_done_1020854c(void)
{
    for (uint32_t port = 0u; port < 2u; ++port) {
        volatile uint32_t *channel =
            gx8002_xip_uart_channel_lookup_10207ac0(port & 0xffu);
        if (channel != (void *)0) {
            (void)gx8002_xip_uart_transmit_abort_102036e8(channel[2]);
            (void)gx8002_xip_uart_receive_abort_10203704(channel[2]);
            channel[3] = 0u;
        }
    }
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002e360), 0u, 0x1c0u);
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002ecc4), 0u, 0x14u);
    gx8002_xip_memset_102099cc(
        (void *)(uintptr_t)UINT32_C(0x2002e050), 0u, 0x2f8u);
    return 0u;
}
