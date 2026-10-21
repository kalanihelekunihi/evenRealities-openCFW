/* Loaded image B native dispatch 0x10003edc..0x10003fb2.
 * Ten jump-table entries at 0x10012a64 were decoded from the pinned image.
 * MMIO bases are architectural product addresses; final hardware effects
 * require a device. Selector 9 reads a source-owned BSS shadow word.
 */
#include <stdint.h>

#ifdef GX_IMAGE_B_MMIO_TEST
extern volatile uint32_t gx8002_image_b_test_mmio_a000[];
extern volatile uint32_t gx8002_image_b_test_mmio_a001[];
#define A000_BASE ((uintptr_t)gx8002_image_b_test_mmio_a000)
#define A001_BASE ((uintptr_t)gx8002_image_b_test_mmio_a001)
#else
#define A000_BASE UINT32_C(0xa0000000)
#define A001_BASE UINT32_C(0xa0010000)
#endif

extern volatile uint32_t gx8002_image_b_platform_shadow_20017398;

static uint32_t read_a000(uint32_t offset)
{
    return *(volatile const uint32_t *)(uintptr_t)(A000_BASE + offset);
}
static uint32_t read_a001(uint32_t offset)
{
    return *(volatile const uint32_t *)(uintptr_t)(A001_BASE + offset);
}
static void store_word(uint8_t *out, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(out + offset) = value;
}
static void store_half(uint8_t *out, uint32_t offset, uint32_t value)
{
    *(uint16_t *)(void *)(out + offset) = (uint16_t)value;
}

int32_t gx8002_image_b_platform_read_10003edc(uint32_t selector, void *result)
{
    uint8_t *out = (uint8_t *)result;
    switch (selector) {
    case 0:
        for (uint32_t i = 0; i < 8u; ++i)
            store_half(out, i * 2u, read_a000(4u + i * 4u));
        break;
    case 1: store_word(out, 0u, read_a000(0x24u)); break;
    case 2: store_word(out, 0u, read_a000(0x28u)); break;
    case 3: store_word(out, 0u, read_a000(0x2cu) & 15u); break;
    case 4: store_word(out, 0u, read_a000(0x34u) & 15u); break;
    case 5:
        out[0] = (uint8_t)(read_a001(0x58u) & 1u);
        store_word(out, 4u, read_a001(0x5cu));
        break;
    case 6: store_word(out, 0u, read_a000(0x30u)); break;
    case 7: {
        uint32_t packed = read_a000(0x48u);
        out[0] = (uint8_t)(read_a000(0x40u) & 1u);
        out[1] = (uint8_t)read_a000(0x44u);
        store_half(out, 4u, read_a000(0x4cu));
        out[2] = (uint8_t)(packed & 15u);
        out[3] = (uint8_t)((packed >> 4) & 15u);
        out[6] = (uint8_t)read_a000(0x50u);
        out[7] = (uint8_t)read_a000(0x54u);
        break;
    }
    case 8: store_word(out, 0u, read_a000(0x38u)); break;
    case 9: store_word(out, 0u, gx8002_image_b_platform_shadow_20017398); break;
    default: return -1;
    }
    return 0;
}
