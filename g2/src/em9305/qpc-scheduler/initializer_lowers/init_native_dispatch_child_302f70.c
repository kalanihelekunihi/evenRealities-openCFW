/* Stock 0x302f70: stores a at word +0xc of the SRAM object 0x8015cc, tail-calls common_radio_bind_30fc10(0x8015cc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uint32_t);
uint32_t opencfw_em9305_dispatch_child_302f70(uint32_t a)
{
  W32(0x8015ccu + 0xcu) = a;
  return opencfw_em9305_common_radio_bind_30fc10(0x8015ccu);
}
