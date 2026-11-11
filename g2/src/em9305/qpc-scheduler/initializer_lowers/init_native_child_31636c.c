/* Stock 0x31636c: phy_start_324680(a); r = phy_schedule_318278(a); byte a[515] = 1; return r.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_phy_start_324680(uint32_t);
extern uint32_t opencfw_em9305_phy_schedule_318278(uint32_t);
uint32_t opencfw_em9305_child_31636c(uint32_t a)
{
  (void)opencfw_em9305_phy_start_324680(a);
  uint32_t r = opencfw_em9305_phy_schedule_318278(a);
  B8(a + 515u) = 1u;
  return r;
}
