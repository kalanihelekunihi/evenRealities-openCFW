#include <stdint.h>

#define CASE_CRITICAL_NEST (*(volatile uint32_t *)(uintptr_t)0x2000019cu)

/* Original 0x0800bffc..0x0800c010. */
void case_enter_critical(void)
{
    __asm__ volatile("cpsid i" : : : "memory");
    CASE_CRITICAL_NEST++;
    __asm__ volatile("dsb sy\n\tisb sy" : : : "memory");
}

/* Original 0x0800c014..0x0800c02c. Zero nesting is nonreturning. */
void case_exit_critical(void)
{
    if (CASE_CRITICAL_NEST != 0u) {
        CASE_CRITICAL_NEST--;
        if (CASE_CRITICAL_NEST == 0u) {
            __asm__ volatile("cpsie i" : : : "memory");
        }
        return;
    }
    __asm__ volatile("cpsid i" : : : "memory");
    for (;;) {
        __asm__ volatile("nop" : : : "memory");
    }
}
