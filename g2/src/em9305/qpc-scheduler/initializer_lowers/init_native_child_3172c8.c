/* Stock 0x3172c8: p = wsf_pool_allocate(a+0xb); returns p ? p+8 : 0.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_pool_allocate(uint32_t);
uint32_t opencfw_em9305_child_3172c8(uint32_t a)
{
  uint32_t p = opencfw_em9305_wsf_pool_allocate(a + 0xbu);
  return p != 0u ? p + 8u : 0u;
}
