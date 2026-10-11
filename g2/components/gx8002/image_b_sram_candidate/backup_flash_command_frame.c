/* SPDX-License-Identifier: MIT
 * Image-B 0x10007790, controller command frame with descriptor prefix.
 * Descriptor bytes at 0x20016d70 are initialized by a separate image stage.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length);

void gx8002_image_b_flash_command_frame_10007790(
    uint32_t prefix_length, const uint8_t *payload, uint32_t payload_length)
{
    volatile uint32_t *const flash =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *const clock_gate =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0300090);
    volatile const uint8_t *const descriptor_prefix =
        (volatile const uint8_t *)(uintptr_t)UINT32_C(0x20016d70);

    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    *clock_gate = 2u;
    flash[0x4cu / 4u] = 0u;
    flash[0x10u / 4u] = 0u;
    flash[0] = 0x407u;
    flash[0x04u / 4u] = payload_length - 1u;
    flash[0x18u / 4u] = 0u;
    flash[0xf4u / 4u] = 0u;
    flash[0x50u / 4u] = 8u;
    flash[0x08u / 4u] = 1u;
    for (uint32_t i = 0u; i < prefix_length; ++i) {
        while ((flash[0x28u / 4u] & 2u) == 0u) { }
        flash[0x60u / 4u] = descriptor_prefix[i];
    }
    flash[0x10u / 4u] = 1u;
    for (uint32_t i = 0u; i < payload_length; ++i) {
        while ((flash[0x28u / 4u] & 2u) == 0u) { }
        flash[0x60u / 4u] = payload[i];
    }
    while (flash[0x20u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    *clock_gate = 3u;
    *clock_gate = 1u;
    flash[0x08u / 4u] = 1u;
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
}
