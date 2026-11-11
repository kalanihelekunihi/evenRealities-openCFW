/* Stock 0x3228e4: returns word[word[r0+0x2c]+0x6c] != 0.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_scan_callback_3228e4(uint32_t a)
{ return W32(W32(a + 0x2cu) + 0x6cu) != 0u; }
