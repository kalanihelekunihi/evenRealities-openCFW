/* SPDX-License-Identifier: MIT
 * Native XIP 0x102055cc register-set-bit helper and 0x10205880
 * NPU reset. Direct disassembly confirms two ordered bit-3 writes.
 */
#include <stdint.h>

void gx8002_xip_register_set_bit_102055cc(uint32_t address, uint32_t bit)
{
    volatile uint32_t *const reg = (volatile uint32_t *)(uintptr_t)address;
    *reg = *reg | (1u << (bit & 31u));
}

void gx8002_xip_npu_reset_10205880(uint32_t base)
{
    gx8002_xip_register_set_bit_102055cc(base + 4u, 3u);
    gx8002_xip_register_set_bit_102055cc(base + 8u, 3u);
}
