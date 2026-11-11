/* Stock 0x322178: sets byte +8 of the object at [r0+36] to 1, then tail-calls callback_32233c(r0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_callback_32233c(uint32_t);
uint32_t opencfw_em9305_callback_322178(uint32_t a)
{ B8(W32(a + 36u) + 8u) = 1u; return opencfw_em9305_callback_32233c(a); }
