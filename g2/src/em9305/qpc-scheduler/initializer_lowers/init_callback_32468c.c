/* Stock 0x32468c: tail call wsf_queue_remove(queue at SRAM (uintptr_t)&em9305_ram_805194).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#include "em9305_ram.h"
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_wsf_queue_remove(uint32_t);
uint32_t opencfw_em9305_init_callback_32468c(void)
{ return opencfw_em9305_wsf_queue_remove((uintptr_t)&em9305_ram_805194); }
