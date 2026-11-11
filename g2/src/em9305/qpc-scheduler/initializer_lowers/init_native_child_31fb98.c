/* Stock 0x31fb98: p = word[a+0x24]; sets byte p+1 to 1; auxiliary_signal_304394(p); returns 0.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_auxiliary_signal_304394(uint32_t);
uint32_t opencfw_em9305_child_31fb98(uint32_t a)
{
  uint32_t p = W32(a + 0x24u);
  B8(p + 1u) = 1u;
  (void)opencfw_em9305_auxiliary_signal_304394(p);
  return 0u;
}
