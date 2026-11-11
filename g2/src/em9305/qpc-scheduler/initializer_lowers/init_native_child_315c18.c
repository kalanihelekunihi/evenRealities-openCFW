/* Stock 0x315c18: w = word[a+636]; if bit 17 clear return a; clear it, word[a+640] = 0; return mode_event_322fdc(a, 0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_mode_event_322fdc(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_315c18(uint32_t a)
{
  uint32_t w = W32(a + 636u);
  if((w & 0x20000u) == 0u) return a;
  W32(a + 636u) = w & ~0x20000u;
  W32(a + 640u) = 0u;
  return opencfw_em9305_mode_event_322fdc(a, 0u);
}
