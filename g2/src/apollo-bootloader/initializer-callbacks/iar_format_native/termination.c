#include <stdint.h>
/* Reconstruct the real IAR abort->semihosting exit path, not a replacement trap.
 * Original abort417c28, exit41b298..41b2a8; no physical trap is executed in tests. */
__attribute__((noreturn)) void opencfw_iar_exit(void) {
    /* Semihosting SYS_EXIT (0x18) with ADP_Stopped_ApplicationExit (0x20026),
     * repeated if a debugger resumes. */
    for (;;) {
        register uint32_t operation __asm__("r0") = 0x18u;
        register uint32_t reason __asm__("r1") = 0x00020026u;
        __asm__ volatile("bkpt #0xab" : : "r"(operation), "r"(reason) : "memory");
    }
}
/* Abort: the status it loads is overwritten by the exit call, so it is the same path. */
__typeof__(opencfw_iar_exit) opencfw_format_abort_contract __attribute__((alias("opencfw_iar_exit")));
