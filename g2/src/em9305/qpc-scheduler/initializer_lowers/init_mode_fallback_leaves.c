/* Stock 0x32cac4, 0x32cacc, 0x32cad4: set byte +12 of the object in r0 to 0x28, 0x1e and 0x30 (r0 returned untouched).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t opencfw_em9305_mode_event_32cac4(uint32_t a)
{
  B8(a + 12u) = 0x28u;
  return a;
}
uint32_t opencfw_em9305_mode_event_32cacc(uint32_t a)
{
  B8(a + 12u) = 0x1eu;
  return a;
}
uint32_t opencfw_em9305_mode_event_32cad4(uint32_t a)
{
  B8(a + 12u) = 0x30u;
  return a;
}
