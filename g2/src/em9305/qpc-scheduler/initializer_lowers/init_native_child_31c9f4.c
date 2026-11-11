/* Stock 0x31c9f4: p = word[a+0x24]; if(p[2] || p[1]) return child_325e84(p, 3); half[p+240] = 0; return child_320354(p).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_325e84(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_320354(uint32_t);
uint32_t opencfw_em9305_child_31c9f4(uint32_t a)
{
  uint32_t p = W32(a + 0x24u);
  if(B8(p + 2u) != 0u || B8(p + 1u) != 0u) return opencfw_em9305_child_325e84(p, 3u);
  H16(p + 240u) = 0u;
  return opencfw_em9305_child_320354(p);
}
