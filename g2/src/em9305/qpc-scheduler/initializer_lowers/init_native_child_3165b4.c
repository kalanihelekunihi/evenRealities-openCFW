/* Stock 0x3165b4: child_325f9c(a); return phy_timer_start_32c7e4(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_325f9c(uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uint32_t);
uint32_t opencfw_em9305_child_3165b4(uint32_t a)
{
  (void)opencfw_em9305_child_325f9c(a);
  return opencfw_em9305_phy_timer_start_32c7e4(a);
}
