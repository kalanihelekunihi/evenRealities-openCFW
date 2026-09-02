/*
 * SPDX-License-Identifier: MIT
 *
 * Reviewable clean-room event dispatcher authenticated at G2 bootloader
 * address 0x0042F38E.
 */

typedef __UINT8_TYPE__ open_cfw_event_u8;
typedef __UINT32_TYPE__ open_cfw_event_u32;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_event_zero_provider_42f2fa(void);
extern void open_cfw_bootloader_event_value_provider_42f204(open_cfw_event_u32 value);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_event_u32 open_cfw_bootloader_event_dispatch_42f38e(
    open_cfw_event_u32 event, open_cfw_event_u32 unused,
    open_cfw_event_u8 *state)
{
    __asm volatile(
        "push {r4, lr}\n"
        "movs r4, #0\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_event_zero\n"
        "cmp r0, #2\n"
        "beq .Lopen_cfw_event_two\n"
        "blo .Lopen_cfw_event_one\n"
        "cmp r0, #4\n"
        "beq .Lopen_cfw_event_four\n"
        "blo .Lopen_cfw_event_three\n"
        "cmp r0, #6\n"
        "beq .Lopen_cfw_event_done\n"
        "blo .Lopen_cfw_event_five\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_zero:\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_one:\n"
        "ldrb r0, [r2]\n"
        "movs r1, r0\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "bne .Lopen_cfw_event_value\n"
        "bl open_cfw_bootloader_event_zero_provider_42f2fa\n"
        "b .Lopen_cfw_event_join\n"
        ".Lopen_cfw_event_value:\n"
        "uxtb r0, r0\n"
        "bl open_cfw_bootloader_event_value_provider_42f204\n"
        ".Lopen_cfw_event_join:\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_two:\n"
        "ldr r0, [pc, #612]\n"
        "str r0, [r2, #4]\n"
        "ldr r0, [pc, #612]\n"
        "str r0, [r2, #8]\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_three:\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_four:\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_five:\n"
        "b .Lopen_cfw_event_done\n"
        ".Lopen_cfw_event_done:\n"
        "movs r0, r4\n"
        "pop {r4, pc}\n"
    );
}

#else

typedef struct open_cfw_event_state {
    open_cfw_event_u8 value;
    open_cfw_event_u8 padding[3];
    open_cfw_event_u32 first_word;
    open_cfw_event_u32 second_word;
} open_cfw_event_state;

typedef void (*open_cfw_event_zero_provider)(void *context);
typedef void (*open_cfw_event_value_provider)(open_cfw_event_u32 value,
                                               void *context);

__attribute__((used, noinline, visibility("default")))
open_cfw_event_u32 open_cfw_bootloader_event_dispatch_42f38e_portable(
    open_cfw_event_u32 event, open_cfw_event_state *state,
    open_cfw_event_zero_provider zero_provider,
    open_cfw_event_value_provider value_provider, void *context,
    open_cfw_event_u32 event_two_first, open_cfw_event_u32 event_two_second)
{
    switch ((open_cfw_event_u8)event) {
    case 1U:
        if (state->value == 0U) {
            zero_provider(context);
        } else {
            value_provider(state->value, context);
        }
        break;
    case 2U:
        state->first_word = event_two_first;
        state->second_word = event_two_second;
        break;
    default:
        break;
    }
    return 0U;
}

#endif
