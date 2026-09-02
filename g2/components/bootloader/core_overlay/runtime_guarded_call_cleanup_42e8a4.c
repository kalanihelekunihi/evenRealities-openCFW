/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room guarded call/cleanup service authenticated at G2
 * bootloader address 0x0042E8A4.
 */

typedef __UINT32_TYPE__ open_cfw_guard_u32;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_guard_u32 open_cfw_bootloader_guarded_call_cleanup_42e8a4(
    open_cfw_guard_u32 first, open_cfw_guard_u32 second,
    open_cfw_guard_u32 third, open_cfw_guard_u32 fourth,
    open_cfw_guard_u32 fifth)
{
    __asm volatile(
        "push {r2, r3, r4, lr}\n"
        "ldr r4, [sp, #16]\n"
        "str r4, [sp]\n"
        "ldr r4, [pc, #24]\n"
        "ldr r4, [r4, #4]\n"
        "blx r4\n"
        "ldr r1, [pc, #20]\n"
        "movs r2, #195\n"
        "str r2, [r1]\n"
        "movs r2, #0\n"
        "ldr r3, [pc, #16]\n"
        "str r2, [r3]\n"
        "movs r2, #0\n"
        "str r2, [r1]\n"
        "pop {r1, r2, r4, pc}\n"
    );
}

#else

typedef open_cfw_guard_u32 (*open_cfw_guard_provider)(
    open_cfw_guard_u32 first, open_cfw_guard_u32 second,
    open_cfw_guard_u32 third, open_cfw_guard_u32 fourth,
    open_cfw_guard_u32 fifth, void *context);

typedef struct open_cfw_guard_state {
    open_cfw_guard_u32 control;
    open_cfw_guard_u32 status;
    open_cfw_guard_u32 write_count;
    open_cfw_guard_u32 write_offsets[3];
    open_cfw_guard_u32 write_values[3];
} open_cfw_guard_state;

static void open_cfw_guard_record(open_cfw_guard_state *state,
                                  open_cfw_guard_u32 offset,
                                  open_cfw_guard_u32 value)
{
    open_cfw_guard_u32 index = state->write_count++;
    if (index < 3U) {
        state->write_offsets[index] = offset;
        state->write_values[index] = value;
    }
}

__attribute__((used, noinline, visibility("default")))
open_cfw_guard_u32 open_cfw_bootloader_guarded_call_cleanup_42e8a4_portable(
    open_cfw_guard_u32 first, open_cfw_guard_u32 second,
    open_cfw_guard_u32 third, open_cfw_guard_u32 fourth,
    open_cfw_guard_u32 fifth, open_cfw_guard_provider provider,
    void *context, open_cfw_guard_state *state)
{
    open_cfw_guard_u32 result = provider(first, second, third, fourth, fifth,
                                         context);
    state->control = 195U;
    open_cfw_guard_record(state, 0U, 195U);
    state->status = 0U;
    open_cfw_guard_record(state, 28U, 0U);
    state->control = 0U;
    open_cfw_guard_record(state, 0U, 0U);
    return result;
}

#endif
