#include <stdint.h>
/* Stock Main 0x541b74 -> 0x585120: fatal formatter constraint path.
 * Evidence: FUN_00585120 @ 0x585120 (16 B sha 6d27b3e4…), corpus
 * apollo-main/ghidra/open-2026-09-29/decomp/00585120.c = software_bkpt(0xab) loop;
 * the exit path encodes semihosting SYS_EXIT 0x18, ADP_Stopped 0x20026 (0x585120..0x585134). */
__attribute__((noreturn)) void g2_main_formatter_exit(void) {
    /* Semihosting SYS_EXIT (0x18) with ADP_Stopped_ApplicationExit (0x20026),
     * repeated if a debugger resumes. */
    for (;;) {
        register uint32_t operation __asm__("r0") = 0x18u;
        register uint32_t reason __asm__("r1") = 0x00020026u;
        __asm__ volatile("bkpt #0xab" : : "r"(operation), "r"(reason) : "memory");
    }
}
/* Abort: the status it loads is overwritten by the exit call, so it is the same path. */
__typeof__(g2_main_formatter_exit) g2_main_formatter_abort __attribute__((alias("g2_main_formatter_exit")));
