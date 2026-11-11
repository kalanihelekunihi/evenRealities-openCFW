/* Stock 0x315d40: phy_complete_32c818(a); return child_32ca3c(a). (r13 keeps a across the first call.)
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_phy_complete_32c818(uint32_t);
extern uint32_t opencfw_em9305_child_32ca3c(uint32_t);
uint32_t opencfw_em9305_child_315d40(uint32_t a)
{
  (void)opencfw_em9305_phy_complete_32c818(a);
  return opencfw_em9305_child_32ca3c(a);
}
