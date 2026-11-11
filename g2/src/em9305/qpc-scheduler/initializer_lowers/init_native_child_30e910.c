/* Stock 0x30e910: ev = 0x19 << 16 on the stack; return ll_event_callback_30e79c(&ev).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uint32_t);
uint32_t opencfw_em9305_child_30e910(void)
{
  uint32_t ev = 0x19u << 16;
  return opencfw_em9305_ll_event_callback_30e79c((uint32_t)(uintptr_t)&ev);
}
