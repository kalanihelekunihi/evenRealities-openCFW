/* Stock 0x3199d8: child_319ea0(a); common_release_304588(1); return command_record_clear_31ac54(a).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_319ea0(uint32_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_command_record_clear_31ac54(uint32_t);
uint32_t opencfw_em9305_child_3199d8(uint32_t a)
{
  (void)opencfw_em9305_child_319ea0(a);
  (void)opencfw_em9305_common_release_304588(1u);
  return opencfw_em9305_command_record_clear_31ac54(a);
}
