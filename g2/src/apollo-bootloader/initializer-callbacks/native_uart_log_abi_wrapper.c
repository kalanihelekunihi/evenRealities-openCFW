/* SPDX-License-Identifier: MIT
 * Stock log-send entry for the console row (row 1). Stock returns a stale
 * register; the caller ignores the result. */
#include <stdint.h>

extern uint32_t opencfw_boot_uart_log_send(uint32_t row, uint32_t borrowed, uint32_t length);

uint32_t opencfw_boot_uart_log_send_ambient_abi(uint32_t borrowed, uint32_t length)
{
    (void)opencfw_boot_uart_log_send(1u, borrowed, length);
    return 0u;
}
