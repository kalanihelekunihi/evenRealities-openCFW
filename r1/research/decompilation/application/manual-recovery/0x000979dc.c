/*
 * Manual semantic recovery for the sole function that Ghidra 12.1.2 could not decompile.
 *
 * Production range: 0x000979dc..0x00097a6d (code), followed by a literal pool through
 * 0x00097a87. The function is called once, from 0x00096518. This translation preserves every
 * observed register access and branch effect but does not claim the original identifier names.
 */
#include <stdint.h>

enum {
    CORTEX_M4_CPUID = 0x410fc241u,
    EXPECTED_CPUID_ADDRESS = 0xe000ed00u,
    NVIC_PRIORITY_BASE = 0xe000e400u,
    RUNTIME_PRIORITY_STATE = 0x20007810u,
    SYSTEM_HANDLER_PRIORITY_2 = 0xe000ed22u,
    SCB_CPACR = 0xe000ed88u,
    FPU_FPCCR = 0xe000ef34u,
    SCB_SCR = 0xe000ed10u,
};

extern void FUN_00095da4(void);
extern void FUN_00027238(void);
extern void FUN_000854e0(void) __attribute__((noreturn));

static void r1_set_basepri(uint32_t value) {
    __asm volatile("msr basepri, %0" : : "r"(value) : "memory");
}

static void r1_fault_forever(void) __attribute__((noreturn));
static void r1_fault_forever(void) {
    r1_set_basepri(0x40u);
    *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    for (;;) {
        __asm volatile("nop");
    }
}

void FUN_000979dc(uint32_t ignored_0, uint32_t ignored_1) {
    (void)ignored_0;
    (void)ignored_1;

    if (*(volatile const uint32_t *)(uintptr_t)EXPECTED_CPUID_ADDRESS != CORTEX_M4_CPUID) {
        r1_fault_forever();
    }

    volatile uint8_t *const priority_register =
        (volatile uint8_t *)(uintptr_t)NVIC_PRIORITY_BASE;
    const uint8_t saved_priority = *priority_register;
    *priority_register = 0xffu;
    uint8_t implemented_mask = *priority_register;

    volatile uint8_t *const priority_state =
        (volatile uint8_t *)(uintptr_t)RUNTIME_PRIORITY_STATE;
    priority_state[0] = (uint8_t)(implemented_mask & 0x02u);
    *(volatile uint32_t *)(uintptr_t)(RUNTIME_PRIORITY_STATE + 8u) = 7u;
    uint32_t priority_bits = 7u;
    while ((implemented_mask & 0x80u) == 0u) {
        implemented_mask = (uint8_t)(implemented_mask << 1);
        priority_bits--;
    }
    *(volatile uint32_t *)(uintptr_t)(RUNTIME_PRIORITY_STATE + 8u) = priority_bits & 7u;
    *priority_register = saved_priority;

    *(volatile uint8_t *)(uintptr_t)SYSTEM_HANDLER_PRIORITY_2 = 0xe0u;
    FUN_00095da4();

    *(volatile uint32_t *)(uintptr_t)(RUNTIME_PRIORITY_STATE + 4u) = 0u;
    *(volatile uint32_t *)(uintptr_t)SCB_CPACR |= 0x00f00000u;
    *(volatile uint32_t *)(uintptr_t)FPU_FPCCR |= 0xc0000000u;
    *(volatile uint32_t *)(uintptr_t)SCB_SCR |= 0x10u;
    FUN_00027238();
    FUN_000854e0();
}
