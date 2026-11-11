/* Stock 0x319978: byte a[0x8d6] = 1; byte a[826] = 0x3c; returns a+826 (incidental r0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_child_319978(uint32_t a)
{
  B8(a + 0x8d6u) = 1u;
  B8(a + 826u) = 0x3cu;
  return a + 826u;
}
