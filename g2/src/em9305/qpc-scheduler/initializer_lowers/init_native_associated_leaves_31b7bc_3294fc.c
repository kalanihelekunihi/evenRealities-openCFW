/* Stock 0x31b7bc, 0x3294fc: predicates: byte[a+621] == 3 and byte[a+623] == 3.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_associated_child_31b7bc(uint32_t a)
{
  return B8(a + 621u) == 3u;
}
uint32_t opencfw_em9305_associated_child_3294fc(uint32_t a)
{
  return B8(a + 623u) == 3u;
}
