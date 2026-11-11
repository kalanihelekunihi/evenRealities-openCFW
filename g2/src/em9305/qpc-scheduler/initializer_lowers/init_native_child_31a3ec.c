/* Stock 0x31a3ec: byte a[2] = 1; tail ll_schedule_notify_313354(byte a[241] ? a+484 : a+244).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uint32_t);
uint32_t opencfw_em9305_child_31a3ec(uint32_t a)
{
  uint32_t f = B8(a + 241u);
  B8(a + 2u) = 1u;
  return opencfw_em9305_ll_schedule_notify_313354(f != 0u ? a + 484u : a + 244u);
}
