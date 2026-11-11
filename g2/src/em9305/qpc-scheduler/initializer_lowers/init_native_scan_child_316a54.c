/* Stock 0x316a54: memset(a, 0, 0x48), then byte a[64] = b; returns memset result.
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_memset(uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_scan_ring_init_316a54(uint32_t a,uint32_t b)
{
  uint32_t r = opencfw_em9305_memset(a, 0u, 0x48u);
  B8(a + 64u) = (uint8_t)b;
  return r;
}
