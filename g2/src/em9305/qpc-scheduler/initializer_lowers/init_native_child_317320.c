/* Stock 0x317320: p = wsf_queue_remove(a+184); if p, wsf_pool_release(p).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_queue_remove(uint32_t);
extern uint32_t opencfw_em9305_wsf_pool_release(uint32_t);
void opencfw_em9305_child_317320(uint32_t a)
{
  uint32_t p = opencfw_em9305_wsf_queue_remove(a + 184u);
  if(p != 0u) (void)opencfw_em9305_wsf_pool_release(p);
}
