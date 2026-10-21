/* SPDX-License-Identifier: MIT
 * Image-B 0x10009d7c initialized audio/runtime SRAM descriptor.
 * Literal addresses and lengths come from the native instruction stream.
 */
#include <stdint.h>

extern void gx8002_image_b_zero_100113c4(void *destination,
                                            uint32_t byte_value,
                                            uint32_t bytes);

void gx8002_image_b_runtime_state_init_at_10009d7c(uintptr_t base_address)
{
    volatile uint32_t *const words = (volatile uint32_t *)base_address;
    uintptr_t ring_address = base_address + UINT32_C(0x80);
    gx8002_image_b_zero_100113c4((void *)base_address, 0u, 120u);
    gx8002_image_b_zero_100113c4((void *)ring_address, 0u, 11264u);

    words[0x00 / 4] = UINT32_C(0x20191222);
    words[0x08 / 4] = 2u;
    words[0x50 / 4] = UINT32_C(0x20030000);
    words[0x54 / 4] = 12288u;
    words[0x18 / 4] = 1u;
    words[0x48 / 4] = UINT32_C(0x2001a380);
    words[0x4c / 4] = 6144u;
    words[0x34 / 4] = 12u;
    words[0x28 / 4] = 12u;
    words[0x6c / 4] = 40u;
    words[0x60 / 4] = 256u;
    words[0x1c / 4] = 16u;
    words[0x44 / 4] = 2784u;
    words[0x20 / 4] = 16000u;
    words[0x40 / 4] = 2816u;
    words[0x0c / 4] = 0u;
    words[0x58 / 4] = 0u;
    words[0x5c / 4] = 0u;
    words[0x10 / 4] = 0u;
    words[0x64 / 4] = 0u;
    words[0x68 / 4] = 0u;
    words[0x2c / 4] = 0u;
    words[0x14 / 4] = 0u;
    words[0x70 / 4] = 0u;
    words[0x74 / 4] = 0u;
    words[0x30 / 4] = 0u;
    words[0x24 / 4] = 3u;
    words[0x38 / 4] = (uint32_t)ring_address;
    words[0x3c / 4] = 4u;
    words[0x04 / 4] = 0u;
}

void gx8002_image_b_runtime_state_init_10009d7c(void)
{
    gx8002_image_b_runtime_state_init_at_10009d7c(
        (uintptr_t)UINT32_C(0x20017700));
}
