/* Stock 0x317a84: copies byte c[1] to a[0] and the little-endian halfword c[2..3] to *b; returns 4.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_dispatch_child_317a84(uint32_t a,uint32_t b,uint32_t c)
{
  B8(a) = B8(c + 1u);
  H16(b) = (uint16_t)((B8(c + 3u) << 8) + B8(c + 2u));
  return 4u;
}
