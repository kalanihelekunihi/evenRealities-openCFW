/* Stock 0x3163cc: sets bit 0 of byte +13, then tail-calls child_322f2c(r0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_322f2c(uint32_t);
uint32_t opencfw_em9305_child_3163cc(uint32_t a)
{ B8(a + 13u) = (uint8_t)(B8(a + 13u) | 1u); return opencfw_em9305_child_322f2c(a); }
