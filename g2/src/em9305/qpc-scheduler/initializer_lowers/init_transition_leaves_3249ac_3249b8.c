/* Stock 0x3249ac, 0x3249b8: 3249ac: byte a[2]=1, tail ll_schedule_notify_313354(a+0x30); 3249b8: tail init_secondary_cleanup_321450(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_cleanup_321450(uint32_t);
uint32_t opencfw_em9305_init_transition_3249ac(uint32_t a)
{
  B8(a + 2u) = 1u;
  return opencfw_em9305_ll_schedule_notify_313354(a + 0x30u);
}
uint32_t opencfw_em9305_init_transition_3249b8(uint32_t a)
{
  return opencfw_em9305_init_secondary_cleanup_321450(a);
}
