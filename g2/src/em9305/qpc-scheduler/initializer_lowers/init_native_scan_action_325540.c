/* Stock 0x325540: tail call command_status_30e8c0(0xc).
 * Converted from the lowered ARC asm; compiled with the g2-em9305-1 profile (-Os) and the
 * disassembly diffed against the stock lowering: identical, or differing only in delay-slot
 * scheduling / a redundant zero-extension / absolute-address ld/st forms (reviewed by hand). */
#include <stdint.h>
#define B8(a)  (*(volatile uint8_t  *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_em9305_command_status_30e8c0(uint32_t);
uint32_t opencfw_em9305_scan_action_325540(void)
{ return opencfw_em9305_command_status_30e8c0(0xcu); }
