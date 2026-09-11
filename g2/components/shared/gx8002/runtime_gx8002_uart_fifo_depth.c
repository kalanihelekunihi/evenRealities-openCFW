/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* The stock helper accepts only one-hot values in parameter bits 23:16.
 * Unsupported encodings return zero, including multi-bit values. */
uint32_t open_cfw_gx8002_uart_fifo_depth(volatile uint32_t *descriptor)
{
    uint32_t device=descriptor[1];
    uint32_t encoding=(*(volatile uint32_t *)(uintptr_t)(device+0xf4u)>>16)&255u;
    if (!encoding || (encoding&(encoding-1u))) return 0;
    return encoding<<4;
}
