/* Stock 0x32c980: tail call memcpy(a+684, SRAM 0x80281c, 0x18).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_memcpy(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_child_32c980(uint32_t a)
{
  return opencfw_em9305_memcpy(a + 684u, 0x80281cu, 0x18u);
}
