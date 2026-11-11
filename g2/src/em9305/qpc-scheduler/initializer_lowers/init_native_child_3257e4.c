/* Stock 0x3257e4: returns (word[word[a+0x2c]+0x6c] != 0) & (b == 0xc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_child_3257e4(uint32_t a,uint32_t b)
{
  return (uint32_t)(W32(W32(a + 0x2cu) + 0x6cu) != 0u) & (uint32_t)(b == 0xcu);
}
