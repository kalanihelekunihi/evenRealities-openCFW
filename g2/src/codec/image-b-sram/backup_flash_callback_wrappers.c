/* Image-B 0x10007f58, 0x10007f64 and 0x10007f78: native flash callback
 * table leaves. These preserve the value returned in r0 by the child. */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_flash_descriptor_20016d60[8];
extern int32_t gx8002_image_b_flash_erase_1000764c(
    uint32_t address, uint32_t length);

uint32_t gx8002_image_b_flash_size_10007f58(void)
{
    const volatile uint32_t *profile =
        (const volatile uint32_t *)(uintptr_t)
            gx8002_image_b_flash_descriptor_20016d60[3];
    return profile[0];
}

/* The 14-way native dispatch at 0x10006eb8 uses the stock jump table
 * 0x10012e00. Repeated entries deliberately share the same result. */
uint32_t gx8002_image_b_flash_query_10006eb8(uint32_t selector)
{
    const volatile uint32_t *profile =
        (const volatile uint32_t *)(uintptr_t)
            gx8002_image_b_flash_descriptor_20016d60[3];
    switch (selector) {
    case 0u: case 12u: return 0u;
    case 1u: return profile[0];
    case 2u: return profile[1];
    case 3u: return gx8002_image_b_flash_descriptor_20016d60[1];
    case 4u: case 6u: case 10u: return 4096u;
    case 5u: case 7u: case 11u:
        return gx8002_image_b_flash_descriptor_20016d60[1] >> 12;
    case 8u: return 256u;
    case 13u: return 1u;
    default: return UINT32_MAX;
    }
}

int32_t gx8002_image_b_flash_erase_all_10007f64(void)
{
    return gx8002_image_b_flash_erase_1000764c(
        0u, gx8002_image_b_flash_descriptor_20016d60[1]);
}

int32_t gx8002_image_b_flash_erase_all_callback_10007f78(void)
{
    return gx8002_image_b_flash_erase_all_10007f64();
}
