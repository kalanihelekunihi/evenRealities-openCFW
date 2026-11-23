/* Stock 0x31a920: child_3203f0(a); returns 0 when byte SRAM ((uintptr_t)&em9305_ram_803560 + 0x1u) is 0, else scan_error_30e7f8(0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_child_3203f0(uint32_t);
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
uint32_t opencfw_em9305_child_31a920(uint32_t a)
{
  (void)opencfw_em9305_child_3203f0(a);
  uint32_t v = B8(((uintptr_t)&em9305_ram_803560 + 0x1u));
  if(v == 0u) return v;
  return opencfw_em9305_scan_error_30e7f8(0u);
}
