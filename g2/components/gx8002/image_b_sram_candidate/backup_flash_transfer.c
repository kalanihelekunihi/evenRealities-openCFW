/* SPDX-License-Identifier: MIT
 * Image-B flash controller byte transactions 0x10006c30/0x10006cb0.
 * Native volatile ordering and wait conditions are retained; no timeout
 * exists in the original bodies.
 */
#include <stdint.h>

static volatile uint32_t *const flash =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);

uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t command, uint8_t *destination, uint32_t length)
{
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0] = 0x0c07u;
    flash[0x04u / 4u] = length - 1u;
    flash[0x10u / 4u] = 1u;
    flash[0x18u / 4u] = 0u;
    flash[0xf4u / 4u] = 0u;
    flash[0x08u / 4u] = 1u;
    flash[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < length; ++i) {
        while ((flash[0x28u / 4u] & 8u) == 0u) { }
        destination[i] = (uint8_t)flash[0x60u / 4u];
    }
    while (flash[0x24u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    return 0u;
}

uint32_t gx8002_image_b_flash_write_10006cb0(
    uint32_t command, const uint8_t *source, uint32_t length)
{
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x10u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0] = 0x0407u;
    flash[0x04u / 4u] = length;
    flash[0x10u / 4u] = 1u;
    flash[0x18u / 4u] = length << 16;
    flash[0xf4u / 4u] = 0u;
    flash[0x08u / 4u] = 1u;
    flash[0x60u / 4u] = command;
    for (uint32_t i = 0u; i < length; ++i) {
        while ((flash[0x28u / 4u] & 2u) == 0u) { }
        flash[0x60u / 4u] = source[i];
    }
    while (flash[0x20u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    return 0u;
}
