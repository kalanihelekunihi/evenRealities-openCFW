/* Stock 0x31fbac: sets byte +3 of the object at [r0+0x24] to 1, then tail-calls child_31fdc4(r0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_31fdc4(uint32_t);
uint32_t opencfw_em9305_child_31fbac(uint32_t a)
{ B8(W32(a + 0x24u) + 3u) = 1u; return opencfw_em9305_child_31fdc4(a); }
