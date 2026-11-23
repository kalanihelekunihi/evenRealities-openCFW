/* Stock 0x31a85c: returns 0 when byte SRAM ((uintptr_t)&em9305_ram_803560 + 0x1u) is 0, else tail-calls scan_error_30e7f8(0xc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_scan_error_30e7f8(uint32_t);
uint32_t opencfw_em9305_child_31a85c(void)
{
  uint32_t v = B8(((uintptr_t)&em9305_ram_803560 + 0x1u));
  if(v == 0u) return v;
  return opencfw_em9305_scan_error_30e7f8(0xcu);
}
