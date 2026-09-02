/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room Cortex-M runtime startup tail authenticated at G2
 * bootloader addresses 0x0043297C through 0x004329D2.
 */

typedef __UINT32_TYPE__ open_cfw_runtime_u32;

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_runtime_u32 open_cfw_bootloader_vector_table_provider_432910(void);
extern void open_cfw_bootloader_init_array_provider_43299c(void);
extern void open_cfw_bootloader_platform_init_provider_41b862(void);
extern void open_cfw_bootloader_terminal_loop_provider_4329c4(void);
extern void open_cfw_bootloader_terminal_service_provider_41b298(open_cfw_runtime_u32);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_runtime_start_43297c(void)
{
    __asm volatile(
        "bl open_cfw_bootloader_vector_table_provider_432910\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "bl open_cfw_bootloader_init_array_provider_43299c\n"
        "1:\n"
        "nop.w\n"
        "movs r0, #0\n"
        "nop.w\n"
        "bl open_cfw_bootloader_platform_init_provider_41b862\n"
        "bl open_cfw_bootloader_terminal_loop_provider_4329c4\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_init_array_run_43299c(void)
{
    __asm volatile(
        "push {r4, lr}\n"
        "ldr r1, [pc, #28]\n"
        "add r1, pc\n"
        "adds r1, #24\n"
        "ldr r4, [pc, #24]\n"
        "add r4, pc\n"
        "adds r4, #22\n"
        "b 2f\n"
        "1:\n"
        "ldr r2, [r1]\n"
        "adds r0, r1, #4\n"
        "add r1, r2\n"
        "blx r1\n"
        "mov r1, r0\n"
        "2:\n"
        "cmp r1, r4\n"
        "bne 1b\n"
        "pop {r4, pc}\n"
    );
}

__attribute__((used, noinline, naked, noreturn, visibility("default")))
void open_cfw_bootloader_terminal_loop_4329c4(void)
{
    __asm volatile(
        "b.w 1f\n"
        "1:\n"
        "mov r7, r0\n"
        "2:\n"
        "mov r0, r7\n"
        "bl open_cfw_bootloader_terminal_service_provider_41b298\n"
        "b 2b\n"
    );
}

#else

typedef open_cfw_runtime_u32 (*open_cfw_runtime_init_fn)(void *context);
typedef void (*open_cfw_runtime_terminal_fn)(open_cfw_runtime_u32 status,
                                              void *context);

typedef struct open_cfw_runtime_startup_state {
    open_cfw_runtime_u32 vector_table_ready;
    open_cfw_runtime_u32 init_calls;
    open_cfw_runtime_u32 platform_init_calls;
    open_cfw_runtime_u32 terminal_status;
} open_cfw_runtime_startup_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_runtime_start_43297c_portable(
    open_cfw_runtime_startup_state *state, open_cfw_runtime_init_fn init,
    void *context)
{
    if (state->vector_table_ready != 0U && init != (open_cfw_runtime_init_fn)0) {
        (void)init(context);
        state->init_calls += 1U;
    }
    state->platform_init_calls += 1U;
    state->terminal_status = 0U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_runtime_u32 open_cfw_bootloader_init_array_run_43299c_portable(
    open_cfw_runtime_init_fn *begin, open_cfw_runtime_init_fn *end,
    void *context)
{
    open_cfw_runtime_u32 calls = 0U;
    while (begin != end) {
        open_cfw_runtime_init_fn function = *begin++;
        if (function != (open_cfw_runtime_init_fn)0) {
            (void)function(context);
            calls += 1U;
        }
    }
    return calls;
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_terminal_loop_4329c4_portable(
    open_cfw_runtime_startup_state *state, open_cfw_runtime_u32 status,
    open_cfw_runtime_terminal_fn service, void *context,
    open_cfw_runtime_u32 bounded_iterations)
{
    state->terminal_status = status;
    while (bounded_iterations-- != 0U) {
        service(status, context);
    }
}

#endif
