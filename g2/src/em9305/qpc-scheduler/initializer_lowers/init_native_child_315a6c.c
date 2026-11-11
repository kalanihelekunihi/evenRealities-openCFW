/* Stock 0x315a6c: clears bit 0 of byte a[13]; child_325cb4(a); return phy_timer_start_32c7e4(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_325cb4(uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uint32_t);
uint32_t opencfw_em9305_child_315a6c(uint32_t a)
{
  B8(a + 13u) = (uint8_t)(B8(a + 13u) & ~1u);
  (void)opencfw_em9305_child_325cb4(a);
  return opencfw_em9305_phy_timer_start_32c7e4(a);
}
