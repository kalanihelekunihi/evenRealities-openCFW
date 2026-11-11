/* Stock 0x3175bc: writes a 4-byte record at a: [0]=1,[1]=b,[2]=c,[3]=c>>8; returns 4.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_child_3175bc(uint32_t a,uint32_t b,uint32_t c)
{
  B8(a + 2u) = (uint8_t)c;
  B8(a + 1u) = (uint8_t)b;
  B8(a + 3u) = (uint8_t)(c >> 8);
  B8(a) = 1u;
  return 4u;
}
