/* Stock 0x315c0c: tail call mode_event_322fdc(r0, byte at SRAM 0x80281d).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_mode_event_322fdc(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_315c0c(uint32_t a)
{ return opencfw_em9305_mode_event_322fdc(a, B8(0x80281du)); }
