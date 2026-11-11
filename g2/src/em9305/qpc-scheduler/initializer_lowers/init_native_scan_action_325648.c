/* Stock 0x325648: tail memcpy(0x805af8, word[0x805c78]+4, 8).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_memcpy(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_scan_action_325648(void)
{
  return opencfw_em9305_memcpy(0x805af8u, W32(0x805c78u) + 4u, 8u);
}
