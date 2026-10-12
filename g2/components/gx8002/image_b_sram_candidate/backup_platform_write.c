/* Loaded image B native dispatch 0x1001574c..0x1001582b.
 * The ten jump-table destinations at 0x10012a3c include an invalid
 * selector 6. `mvc` stores comparison flag C as 0/1, per pinned C-SKY
 * translator; the selector-7 register write order follows native bytes.
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

static void write_a000(uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)(A000_BASE + offset) = value;
}
static void write_a001(uint32_t offset, uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)(A001_BASE + offset) = value;
}
static uint32_t word_at(const uint8_t *input, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(input + offset);
}
static uint16_t half_at(const uint8_t *input, uint32_t offset)
{
    return *(const uint16_t *)(const void *)(input + offset);
}

int32_t gx8002_image_b_platform_write_1001574c(
    uint32_t selector, const void *value)
{
    const uint8_t *input = (const uint8_t *)value;
    switch (selector) {
    case 0:
        for (uint32_t i = 0; i < 8u; ++i)
            write_a000(4u + i * 4u, half_at(input, i * 2u));
        break;
    case 1: write_a000(0x24u, word_at(input, 0u)); break;
    case 2: write_a000(0x28u, word_at(input, 0u)); break;
    case 3: write_a000(0x2cu, word_at(input, 0u)); break;
    case 4: write_a000(0x34u, word_at(input, 0u)); break;
    case 5:
        write_a001(0x58u, input[0] & 1u);
        write_a001(0x5cu, word_at(input, 4u));
        break;
    case 7: {
        uint32_t high_nibble = (uint32_t)input[3] << 4;
        uint32_t packed = high_nibble | input[2];
        uint8_t one = input[1];
        uint8_t zero = input[0];
        uint16_t half = half_at(input, 4u);
        write_a000(0x4cu, half);
        write_a000(0x48u, packed);
        write_a000(0x44u, one != 0u);
        write_a000(0x40u, zero != 0u);
        break;
    }
    case 8: write_a000(0x38u, word_at(input, 0u)); break;
    case 9: {
        volatile const uint32_t *in = (volatile const uint32_t *)value;
        write_a000(0x3cu, in[0] & 1u);
        gx8002_image_b_platform_shadow_20017398 = in[0] & 1u;
        break;
    }
    default: return -1;
    }
    return 0;
}
