/* SPDX-License-Identifier: MIT. Independent reconstruction of 0x41c838..0x41c860. */
#include <stdint.h>
uint32_t opencfw_boot_ton_gate_write(uint32_t argument)
{
    volatile uint32_t *control = (volatile uint32_t *)(uintptr_t)0x40020060;
    uint32_t byte = (uint8_t)argument;
    *control = (*control & ~(1u << 16)) | ((byte & 1u) << 16);
    *control = (*control & ~1u) | (byte & 1u);
    *control = (*control & ~(1u << 5)) | ((byte & 1u) << 5);
    return byte;
}
