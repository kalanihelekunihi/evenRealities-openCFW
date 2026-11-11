/* Stock 0x30e7ec: stores 0x17<<16 at [r0], tail-calls ll_event_callback_30e79c(r0).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uint32_t);
uint32_t opencfw_em9305_stream_stop_30e7ec(uint32_t a)
{ W32(a) = 0x17u << 16; return opencfw_em9305_ll_event_callback_30e79c(a); }
