/* Native clock 0x310900..0x310914 and the shared products. Stock uses the
 * ARCv2 DSP major-6 minor-0x1c / 0x1e operations (binutils: MPYWHL /
 * MPYWHUL): low 32 bits of a 32 x 16 product, the 16-bit operand sign- /
 * zero-extended (g2/docs/em9305-arc-harness.md, wave 28 model). */
#include <stdint.h>
uint32_t opencfw_em9305_sleep_metadata_clock(uint32_t incoming)
{
 (void)incoming;
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 uint32_t scale=*(volatile uint8_t *)(uintptr_t)0xf01804u+1u;
 return value*(uint32_t)(int32_t)(int16_t)scale;
}

/* Shared native MPYWHL: value * sign-extended scale[15:0], low word. */
uint32_t opencfw_em9305_native_clock_product(uint32_t value,uint32_t scale)
{
 return value*(uint32_t)(int32_t)(int16_t)scale;
}

/* Shared native MPYWHUL: value * zero-extended factor[15:0], low word. */
uint32_t opencfw_em9305_native_config_product(uint32_t value,uint32_t factor)
{
 return value*(uint16_t)factor;
}
