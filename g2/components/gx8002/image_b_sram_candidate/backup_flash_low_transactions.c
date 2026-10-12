/* Native image-B flash descriptor low transaction 0x10006d90.
 * Controller word transfer keeps the original register write order and
 * unbounded hardware waits. No external flash outcome is synthesized. */
#include <stdint.h>

extern uint32_t gx8002_image_b_flash_read_10006c30(
    uint32_t, uint8_t *, uint32_t);

uint32_t gx8002_image_b_flash_callback_low_read_10006d90(
    uint32_t command, const uint32_t *source, uint32_t bytes)
{
    volatile uint32_t *flash =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *aux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2800074);

    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x10u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0] = UINT32_C(0x0080041f);
    uint32_t words = bytes >> 2;
    flash[0x04u / 4u] = words - 1u;
    flash[0x10u / 4u] = 1u;
    flash[0x18u / 4u] = UINT32_C(0x00020000);
    *aux = UINT32_C(0x40000218);
    flash[0x50u / 4u] = 8u;
    flash[0x4cu / 4u] = 2u;
    flash[0x08u / 4u] = 1u;
    flash[0x64u / 4u] = 50u;
    flash[0x64u / 4u] = command;
    for (uint32_t i = 0u; i < words; ++i) {
        while ((flash[0x28u / 4u] & 2u) == 0u) { }
        flash[0x60u / 4u] = source[i];
    }
    while (flash[0x20u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    uint8_t status;
    do {
        (void)gx8002_image_b_flash_read_10006c30(5u, &status, 1u);
    } while ((status & 1u) != 0u);
    flash[0x08u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0x08u / 4u] = 1u;
    return 0u;
}

uint32_t gx8002_image_b_flash_callback_low_write_100074ec(
    uint32_t command, uint32_t *destination, uint32_t bytes)
{
    if (bytes == 0u) return 0u;
    volatile uint32_t *flash =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *aux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2800074);
    extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];

    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0x10u / 4u] = 0u;
    flash[0] = UINT32_C(0x0080081f);
    uint32_t words = bytes >> 2;
    flash[0x04u / 4u] = words - 1u;
    flash[0x18u / 4u] = 0u;
    flash[0x54u / 4u] = 7u;
    flash[0x4cu / 4u] = 1u;

    volatile uint32_t *profile = (volatile uint32_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    uint32_t family = profile[1] + UINT32_C(0xffe3c7ee);
    if (family < 2u) {
        *aux = UINT32_C(0x40003219);
        flash[0x08u / 4u] = 1u;
        flash[0x64u / 4u] = 235u;
    } else {
        *aux = UINT32_C(0x40004218);
        flash[0x08u / 4u] = 1u;
        flash[0x64u / 4u] = 107u;
    }
    flash[0x64u / 4u] = command;
    flash[0x10u / 4u] = 1u;
    for (uint32_t i = 0u; i < words; ++i) {
        while ((flash[0x28u / 4u] & 8u) == 0u) { }
        destination[i] = flash[0x60u / 4u];
    }
    while (flash[0x24u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0x08u / 4u] = 1u;
    return 0u;
}
