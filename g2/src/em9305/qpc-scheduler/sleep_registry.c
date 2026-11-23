/* Native sleep registry/head/finalizer 0x3108f4,0x3117f8..0x31183c,
 * 0x311848..0x311876. Direct volatile widths and native IRQ/NOP operations.
 * Compilation does not establish physical timer behavior. */
#include <stdint.h>
#include "em9305_ram.h"
uintptr_t opencfw_em9305_sleep_metadata_head(uint32_t incoming)
{ (void)incoming; return em9305_ram_801994.u32_801998; }
uint32_t opencfw_em9305_sleep_register(uintptr_t callback)
{ em9305_ram_805be0.u32_805c2c=(uint32_t)callback; return (uint32_t)callback; }
static uint32_t latch(void)
{
 uint32_t irq; irq=(uint32_t)__builtin_arc_clri(); __builtin_arc_sync();
 *(volatile uint32_t *)(uintptr_t)0xf01c00u=1;
 __builtin_arc_nop();
 uint32_t status=*(volatile uint32_t *)(uintptr_t)0xf01c08u;
 __builtin_arc_seti((int)irq);
 return status&1u;
}
uint32_t opencfw_em9305_sleep_finalize(uint32_t incoming)
{
 (void)incoming;
 volatile uint32_t *config=&em9305_ram_801994.u32_8019b0;
 *(volatile uint32_t *)(uintptr_t)0xf01c10u=config[1];
 *(volatile uint32_t *)(uintptr_t)0xf01c0cu=config[0];
 uint32_t high=config[1],low=config[0];
 volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0xf01c04u;
 uint32_t old=*control; *control=old&~3u;
 old=*control; *control=old|((high!=0u)<<1u)|(low!=0u);
 return latch();
}
