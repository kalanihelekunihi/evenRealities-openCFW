/* Stock 0x319970: tail call command_rows_status_30e7ac(byte[r0+1], 0xc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_command_rows_status_30e7ac(uint32_t,uint32_t);
uint32_t opencfw_em9305_child_319970(uint32_t a)
{ return opencfw_em9305_command_rows_status_30e7ac(B8(a + 1u), 0xcu); }
