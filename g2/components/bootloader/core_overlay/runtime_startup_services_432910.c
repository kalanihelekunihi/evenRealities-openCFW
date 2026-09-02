/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room Cortex-M startup services authenticated at G2
 * bootloader addresses 0x00432910 through 0x0043297A.
 */

typedef __UINT32_TYPE__ open_cfw_startup_u32;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_process_stack_provider_43293c(void);
extern void open_cfw_bootloader_fpu_provider_432958(void);
extern void open_cfw_bootloader_runtime_start_43297c(void);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_startup_u32 open_cfw_bootloader_vector_table_relocate_432910(void)
{
    __asm volatile(
        "ldr r0, [pc, #24]\n"
        "ldr r1, [pc, #28]\n"
        "str r0, [r1]\n"
        "movs r0, #1\n"
        "bx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_stack_limits_init_43291a(void)
{
    __asm volatile(
        "ldr r0, [pc, #24]\n"
        "msr msplim, r0\n"
        "msr psplim, r0\n"
        "bl open_cfw_bootloader_process_stack_provider_43293c\n"
        "bx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_process_stack_init_43293c(void)
{
    __asm volatile(
        "ldr r0, [pc, #20]\n"
        "mov r1, r0\n"
        "push {r0, r1}\n"
        "mov r0, sp\n"
        "msr psp, r0\n"
        "nop.w\n"
        "bl open_cfw_bootloader_fpu_provider_432958\n"
        "bl open_cfw_bootloader_runtime_start_43297c\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_fpu_enable_432958(void)
{
    __asm volatile(
        "movw r1, #0xed88\n"
        "movt r1, #0xe000\n"
        "ldr r0, [r1]\n"
        "orr r0, r0, #0xf00000\n"
        "str r0, [r1]\n"
        "dsb sy\n"
        "isb sy\n"
        "mov.w r0, #0x2040000\n"
        "vmsr fpscr, r0\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_startup_state {
    open_cfw_startup_u32 vector_table;
    open_cfw_startup_u32 main_stack_limit;
    open_cfw_startup_u32 process_stack_limit;
    open_cfw_startup_u32 process_stack;
    open_cfw_startup_u32 coprocessor_access;
    open_cfw_startup_u32 floating_point_status;
    open_cfw_startup_u32 process_stack_initialized;
    open_cfw_startup_u32 runtime_started;
} open_cfw_startup_state;

__attribute__((used, noinline, visibility("default")))
open_cfw_startup_u32 open_cfw_bootloader_vector_table_relocate_432910_portable(
    open_cfw_startup_state *state)
{
    state->vector_table = 0x00410000U;
    return 1U;
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_stack_limits_init_43291a_portable(
    open_cfw_startup_state *state, open_cfw_startup_u32 limit)
{
    state->main_stack_limit = limit;
    state->process_stack_limit = limit;
    state->process_stack_initialized = 1U;
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_process_stack_init_43293c_portable(
    open_cfw_startup_state *state, open_cfw_startup_u32 process_stack)
{
    state->process_stack = process_stack - 8U;
    state->process_stack_initialized = 1U;
    state->runtime_started = 1U;
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_fpu_enable_432958_portable(
    open_cfw_startup_state *state)
{
    state->coprocessor_access |= 0x00f00000U;
    state->floating_point_status = 0x02040000U;
}

#endif
