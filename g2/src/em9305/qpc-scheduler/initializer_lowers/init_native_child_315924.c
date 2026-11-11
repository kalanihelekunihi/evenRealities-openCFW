/* Stock 0x315924: tail call child_322dd8(r0, 0xc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_322dd8(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_315924(uint32_t a)
{ return opencfw_em9305_child_322dd8(a, 0xcu); }
