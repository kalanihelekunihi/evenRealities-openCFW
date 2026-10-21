/* Native clock 0x310900..0x310914. Preserve major-6 minor-0x1c
 * three-register instruction rather than infer its arithmetic semantics.
 * EM9305 vendor datasheet confirms DSP pipeline; binutils names encoding
 * MPYWHL. Producing runtime semantics are not verified here. */
#include <stdint.h>
__asm__(".extInstruction opencfw_clock_product,6,0x1c,SUFFIX_NONE,SYNTAX_3OP");
uint32_t opencfw_em9305_sleep_metadata_clock(uint32_t incoming)
{
 (void)incoming;
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0xf01808u;
 uint32_t scale=*(volatile uint8_t *)(uintptr_t)0xf01804u+1u;
 uint32_t result;
 __asm__ volatile("opencfw_clock_product %0,%1,%2" : "=r"(result) : "r"(value),"r"(scale));
 return result;
}

/* Shared native major-6/minor-0x1c operation; arithmetic unspecified. */
uint32_t opencfw_em9305_native_clock_product(uint32_t value,uint32_t scale)
{
 uint32_t result;
 __asm__ volatile("opencfw_clock_product %0,%1,%2" : "=r"(result) : "r"(value),"r"(scale));
 return result;
}

__asm__(".extInstruction opencfw_config_product,6,0x1e,SUFFIX_NONE,SYNTAX_3OP");
uint32_t opencfw_em9305_native_config_product(uint32_t value,uint32_t factor)
{
 uint32_t result;
 __asm__ volatile("opencfw_config_product %0,%1,%2" : "=r"(result) : "r"(value),"r"(factor));
 return result;
}
