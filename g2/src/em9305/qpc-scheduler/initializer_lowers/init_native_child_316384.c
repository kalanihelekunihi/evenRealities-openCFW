/* Stock 0x316384: r = phy_reject_32698c(a, 0x23, 1); byte a[834] = 0; return r.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_phy_reject_32698c(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_child_316384(uint32_t a)
{
  uint32_t r = opencfw_em9305_phy_reject_32698c(a, 0x23u, 1u);
  B8(a + 834u) = 0u;
  return r;
}
