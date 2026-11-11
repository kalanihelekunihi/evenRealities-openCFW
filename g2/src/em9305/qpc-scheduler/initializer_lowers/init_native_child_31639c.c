/* Stock 0x31639c: tail call phy_reject_32698c(r0, 0x23, 1).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_phy_reject_32698c(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_child_31639c(uint32_t a)
{ return opencfw_em9305_phy_reject_32698c(a, 0x23u, 1u); }
