/* Stock 0x32a770: sets byte [word[a+0x24]+0xae3] to 1, then tail-calls child_32aa9c(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_32aa9c(uint32_t);
uint32_t opencfw_em9305_child_32a770(uint32_t a)
{
  B8(W32(a + 0x24u) + 0xae3u) = 1u;
  return opencfw_em9305_child_32aa9c(a);
}
