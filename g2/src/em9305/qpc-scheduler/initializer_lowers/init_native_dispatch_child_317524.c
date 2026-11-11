/* Stock 0x317524: tail call ll_event_enqueue(a+8, c, b-0xa).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_ll_event_enqueue(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_dispatch_child_317524(uint32_t a,uint32_t b,uint32_t c)
{
  return opencfw_em9305_ll_event_enqueue(a + 8u, c, b - 0xau);
}
