/* Native image-B 0x10007bd4..0x10007c88: read up to 16 flash info bytes.
 * This is the callback stored at the final table word 0x10016df8. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];

int32_t gx8002_image_b_flash_info_read_10007bd4(
    uint8_t *destination, uint32_t requested, uint32_t *actual)
{
    volatile uint8_t *profile = (volatile uint8_t *)(uintptr_t)
        gx8002_image_b_flash_descriptor_20016d60[3];
    uint32_t manufacturer = profile[6];
    if (manufacturer != 133u && manufacturer != 94u) {
        *actual = 0u;
        return -1;
    }
    uint32_t count = (int32_t)requested < 16 ? requested : 16u;
    *actual = count;

    volatile uint32_t *flash =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2000000);
    volatile uint32_t *aux =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa2800074);
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    flash[0x08u / 4u] = 0u;
    flash[0x4cu / 4u] = 0u;
    flash[0] = 3079u;
    flash[0x04u / 4u] = count - 1u;
    flash[0x10u / 4u] = 1u;
    flash[0x18u / 4u] = UINT32_C(0x00040000);
    *aux = 0u;
    flash[0x08u / 4u] = 1u;
    flash[0x60u / 4u] = 75u;
    flash[0x60u / 4u] = 0u;
    flash[0x60u / 4u] = 0u;
    flash[0x60u / 4u] = 0u;
    flash[0x60u / 4u] = 0u;
    for (uint32_t i = 0u; i < count; ++i) {
        while ((flash[0x28u / 4u] & 8u) == 0u) { }
        destination[i] = (uint8_t)flash[0x60u / 4u];
    }
    while (flash[0x24u / 4u] != 0u) { }
    while ((flash[0x28u / 4u] & 1u) != 0u) { }
    return 0;
}
