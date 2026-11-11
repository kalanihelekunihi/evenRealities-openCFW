/* Stock 0x31a900: tail scan_error_30e7f8(byte SRAM 0x803561 != 0 ? 0xc : 0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
uint32_t opencfw_em9305_child_31a900(void)
{
  return opencfw_em9305_scan_error_30e7f8(B8(0x803561u) != 0u ? 0xcu : 0u);
}
