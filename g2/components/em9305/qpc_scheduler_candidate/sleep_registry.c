/* Native sleep registry/head/finalizer 0x3108f4,0x3117f8..0x31183c,
 * 0x311848..0x311876. Direct volatile widths and native IRQ/NOP operations.
 * Compilation does not establish physical timer behavior. */
#include <stdint.h>
uintptr_t opencfw_em9305_sleep_metadata_head(uint32_t incoming)
{ (void)incoming; return *(volatile uint32_t *)(uintptr_t)0x801998u; }
uint32_t opencfw_em9305_sleep_register(uintptr_t callback)
{ *(volatile uint32_t *)(uintptr_t)0x805c2cu=(uint32_t)callback; return (uint32_t)callback; }
static uint32_t latch(void)
{
 uint32_t irq; __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
 *(volatile uint32_t *)(uintptr_t)0xf01c00u=1;
 __asm__ volatile("nop" ::: "memory");
 uint32_t status=*(volatile uint32_t *)(uintptr_t)0xf01c08u;
 __asm__ volatile("seti %0" :: "r"(irq) : "memory");
 return status&1u;
}
uint32_t opencfw_em9305_sleep_finalize(uint32_t incoming)
{
 (void)incoming;
 volatile uint32_t *config=(volatile uint32_t *)(uintptr_t)0x8019b0u;
 *(volatile uint32_t *)(uintptr_t)0xf01c10u=config[1];
 *(volatile uint32_t *)(uintptr_t)0xf01c0cu=config[0];
 uint32_t high=config[1],low=config[0];
 volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0xf01c04u;
 uint32_t old=*control; *control=old&~3u;
 old=*control; *control=old|((high!=0u)<<1u)|(low!=0u);
 return latch();
}
