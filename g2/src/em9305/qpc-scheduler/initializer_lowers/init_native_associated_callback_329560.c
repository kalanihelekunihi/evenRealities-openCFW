/* Stock 0x329560: associated_reset_32ae50(word[a+0x24]); return associated_callback_329888(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_associated_reset_32ae50(uint32_t);
extern uint32_t opencfw_em9305_associated_callback_329888(uint32_t);
uint32_t opencfw_em9305_associated_callback_329560(uint32_t a)
{
  (void)opencfw_em9305_associated_reset_32ae50(W32(a + 0x24u));
  return opencfw_em9305_associated_callback_329888(a);
}
