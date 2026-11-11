/* Stock 0x319958: child_319ea0(a); common_release_304588(1); return command_rows_status_30e7ac(a[1], 0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_319ea0(uint32_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_command_rows_status_30e7ac(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_319958(uint32_t a)
{
  (void)opencfw_em9305_child_319ea0(a);
  (void)opencfw_em9305_common_release_304588(1u);
  return opencfw_em9305_command_rows_status_30e7ac(B8(a + 1u), 0u);
}
