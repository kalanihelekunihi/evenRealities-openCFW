/* Stock R1 2.2.6.0009 exception entries 0x274ac..0x274e7.
 * Exception LR is EXC_RETURN and SP is the handler stack at entry. A normal
 * C prologue would change SP before CmBacktrace observes it, so the five
 * architectural register handoffs use compiler-supported inline assembly.
 * The diagnostic and reset sequence itself is C. */
#include <stdint.h>

extern void cm_backtrace_fault(uint32_t exception_lr, uint32_t exception_sp);
extern uint32_t r1_reset_trace_persist_tag_write(uint32_t tag);
extern uint32_t r1_reset_trace_current_site_capture(void);
extern _Noreturn void r1_manager_system_reset(void);

__attribute__((noreturn, noinline, used))
void r1_fault_reset_adapter(void)
{
    (void)r1_reset_trace_persist_tag_write(7u);
    (void)r1_reset_trace_current_site_capture();
    r1_manager_system_reset();
}

__attribute__((noreturn, noinline, used))
void r1_fault_entry(uint32_t exception_lr, uint32_t exception_sp)
{
    cm_backtrace_fault(exception_lr, exception_sp);
    r1_fault_reset_adapter();
}

#define R1_FAULT_VECTOR(name) \
    __attribute__((naked, noreturn)) void name(void) \
    { \
        __asm__ volatile("mov r0, lr\n" \
                         "mov r1, sp\n" \
                         "b r1_fault_entry\n"); \
    }

R1_FAULT_VECTOR(NMI_Handler)
R1_FAULT_VECTOR(HardFault_Handler)
R1_FAULT_VECTOR(MemoryManagement_Handler)
R1_FAULT_VECTOR(BusFault_Handler)
R1_FAULT_VECTOR(UsageFault_Handler)
