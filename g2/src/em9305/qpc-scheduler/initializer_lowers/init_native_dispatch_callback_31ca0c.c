/* Stock 0x31ca0c: memset((uintptr_t)&em9305_ram_8029ac, 0, 0x88); return dispatch_callback_31ceb4(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_memset(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_callback_31ceb4(uint32_t);
uint32_t opencfw_em9305_dispatch_callback_31ca0c(uint32_t a)
{
  (void)opencfw_em9305_memset((uintptr_t)&em9305_ram_8029ac, 0u, 0x88u);
  return opencfw_em9305_dispatch_callback_31ceb4(a);
}
