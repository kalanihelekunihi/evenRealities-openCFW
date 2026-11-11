/* Stock 0x325284: 4-entry byte ring: a[a[4]] = v; a[5]++; a[4] = (a[4]+1)==4 ? 0 : a[4]+1.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
void opencfw_em9305_child_325284(uint32_t a, uint32_t v)
{
  uint32_t i = B8(a + 4u);
  B8(a + i) = (uint8_t)v;
  uint32_t n = B8(a + 5u);
  uint32_t m = B8(a + 4u) + 1u;
  if(m == 4u) m = 0u;
  B8(a + 5u) = (uint8_t)(n + 1u);
  B8(a + 4u) = (uint8_t)m;
}
