/* Stock 0x31694c: wsf_critical_enter(); decrement byte SRAM ((uintptr_t)&em9305_ram_805af0 + 0x11u); return wsf_critical_exit().
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define H16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
uint32_t opencfw_em9305_pawr_queue_resume_31694c(void)
{
  (void)opencfw_em9305_wsf_critical_enter();
  uint8_t v = (uint8_t)(B8(((uintptr_t)&em9305_ram_805af0 + 0x11u)) - 1u);
  B8(((uintptr_t)&em9305_ram_805af0 + 0x11u)) = v;
  return opencfw_em9305_wsf_critical_exit();
}
