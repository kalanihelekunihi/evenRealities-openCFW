/*
 * MIT-licensed CmBacktrace-compatible Cortex-M fault-entry glue.
 *
 * The register contract is the same as the vendored upstream IAR handler:
 * r0 receives EXC_RETURN (lr), r1 receives the current exception stack
 * pointer, cm_backtrace_fault() never returns in production, and a defensive
 * loop catches an unexpected return.  Keeping a distinct symbol prevents an
 * unvalidated vector-table takeover.
 */
#include "runtime_cmbacktrace_fault_entry.h"

#if !defined(__arm__) && !defined(__thumb__)
#error "CmBacktrace fault entry requires an Arm Thumb target"
#endif

extern void cm_backtrace_fault(unsigned long fault_handler_lr,
                               unsigned long fault_handler_sp);

__attribute__((naked, noreturn))
void open_cfw_cmbacktrace_hardfault_entry(void)
{
    __asm volatile(
        "mov r0, lr\n"
        "mov r1, sp\n"
        "bl cm_backtrace_fault\n"
        "1: b 1b\n");
}
