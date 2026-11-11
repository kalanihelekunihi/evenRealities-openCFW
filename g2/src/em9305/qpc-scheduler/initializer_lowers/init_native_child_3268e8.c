/* Stock 0x3268e8: p = phy_packet_alloc_32d2f0(1); if p: byte p[0] = 19; return phy_packet_send_32d32c(a, p); else return 0.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_3268e8(uint32_t a)
{
  uint32_t p = opencfw_em9305_phy_packet_alloc_32d2f0(1u);
  if(p == 0u) return p;
  B8(p) = 19u;
  return opencfw_em9305_phy_packet_send_32d32c(a, p);
}
