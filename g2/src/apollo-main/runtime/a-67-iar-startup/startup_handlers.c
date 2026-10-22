/* Main-image reset and default exception handlers (Ambiq startup_iar.c style;
 * no source path is retained). Native 0x5e4232..0x5e4241 (literal 0x5e424c)
 * and 0x5e4250..0x5e4251.
 *
 * Vector slot 1 (ROM 0x438004) holds 0x5e4233; every unused system/IRQ slot
 * (for example ROM 0x438030 DebugMon and 0x438040..0x438064) holds 0x5e4251.
 * The inventory sizes the reset handler as two bytes; it really runs to
 * 0x5e4241 (MSPLIM/PSPLIM = 0x2007d000, the CSTACK base below the initial
 * MSP 0x2007fb00, then the IAR program entry 0x5e4254). */
#include <stdint.h>

#define G2_MAIN_STACK_LIMIT 0x2007d000u

extern void iar_program_start_5e4254(void);

void reset_handler_5e4232(void)
{
    __asm volatile("msr msplim, %0\n\tmsr psplim, %0" : : "r"(G2_MAIN_STACK_LIMIT) : "memory");
    iar_program_start_5e4254();
}

/* am_default_isr: a single `b .`. */
void am_default_isr_5e4250(void)
{
    for (;;) {
    }
}
