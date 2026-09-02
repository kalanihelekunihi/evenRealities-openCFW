/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room state adjustment, floating-point range update, and event
 * dispatch services authenticated at G2 bootloader addresses 0x0042CDF8,
 * 0x0042CED8, and 0x0042D562.
 */

typedef __UINT8_TYPE__ open_cfw_state_u8;
typedef __UINT32_TYPE__ open_cfw_state_u32;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_state_apply_42cea4(open_cfw_state_u32 state);
extern open_cfw_state_u32 open_cfw_bootloader_state_event_zero_42cfe0(
    open_cfw_state_u32 state);
extern open_cfw_state_u32 open_cfw_bootloader_state_event_one_zero_42d3bc(
    open_cfw_state_u32 state);
extern open_cfw_state_u32 open_cfw_bootloader_state_event_one_value_42d104(
    open_cfw_state_u32 state);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_state_adjust_42cdf8(open_cfw_state_u32 state)
{
    __asm volatile(
        "movs r2, #0\n"
        "movs r1, #0\n"
        "movs r1, #0\n"
        "ldr.w r1, [pc, #2464]\n"
        "ldrb r1, [r1]\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_adjust_done\n"
        "ldr.w r1, [pc, #2456]\n"
        "ldr r1, [r1]\n"
        "ubfx r1, r1, #4, #2\n"
        "cmp r1, #3\n"
        "bne .Lopen_cfw_adjust_done\n"
        "ldr.w r1, [pc, #2448]\n"
        "ldr r1, [r1]\n"
        "ubfx r1, r1, #18, #1\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_adjust_no_bias\n"
        "ldr.w r1, [pc, #2436]\n"
        "ldrb r1, [r1]\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_adjust_no_bias\n"
        "movs r1, #1\n"
        "b .Lopen_cfw_adjust_bias_ready\n"
        ".Lopen_cfw_adjust_no_bias:\n"
        "movs r1, #0\n"
        ".Lopen_cfw_adjust_bias_ready:\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq .Lopen_cfw_adjust_select\n"
        "movs r2, #15\n"
        ".Lopen_cfw_adjust_select:\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_adjust_ten_zero\n"
        "cmp r0, #2\n"
        "beq .Lopen_cfw_adjust_zero_two\n"
        "blo .Lopen_cfw_adjust_ten_one\n"
        "b .Lopen_cfw_adjust_zero_other\n"
        ".Lopen_cfw_adjust_ten_zero:\n"
        "movs r0, #10\n"
        "b .Lopen_cfw_adjust_delta\n"
        ".Lopen_cfw_adjust_ten_one:\n"
        "movs r0, #10\n"
        "b .Lopen_cfw_adjust_delta\n"
        ".Lopen_cfw_adjust_zero_two:\n"
        "movs r0, #0\n"
        "b .Lopen_cfw_adjust_delta\n"
        ".Lopen_cfw_adjust_zero_other:\n"
        "movs r0, #0\n"
        ".Lopen_cfw_adjust_delta:\n"
        "subs r1, r0, r2\n"
        "cmp r1, #1\n"
        "blt .Lopen_cfw_adjust_increase\n"
        "subs r2, r0, r2\n"
        "ldr.w r0, [pc, #2380]\n"
        "ldr r1, [r0]\n"
        "cmp r2, r1\n"
        "bhs .Lopen_cfw_adjust_floor_zero\n"
        "ldr r0, [r0]\n"
        "subs r2, r0, r2\n"
        "b .Lopen_cfw_adjust_store_lower\n"
        ".Lopen_cfw_adjust_floor_zero:\n"
        "movs r2, #0\n"
        ".Lopen_cfw_adjust_store_lower:\n"
        "ldr.w r0, [pc, #2368]\n"
        "ldr r1, [r0]\n"
        "bfi r1, r2, #0, #7\n"
        "str r1, [r0]\n"
        "b .Lopen_cfw_adjust_done\n"
        ".Lopen_cfw_adjust_increase:\n"
        "subs r2, r2, r0\n"
        "ldr.w r0, [pc, #2348]\n"
        "ldr r1, [r0]\n"
        "adds r1, r2, r1\n"
        "cmp r1, #128\n"
        "blo .Lopen_cfw_adjust_use_sum\n"
        "movs r2, #127\n"
        "b .Lopen_cfw_adjust_store_upper\n"
        ".Lopen_cfw_adjust_use_sum:\n"
        "ldr r0, [r0]\n"
        "adds r2, r2, r0\n"
        ".Lopen_cfw_adjust_store_upper:\n"
        "ldr.w r0, [pc, #2332]\n"
        "ldr r1, [r0]\n"
        "bfi r1, r2, #0, #7\n"
        "str r1, [r0]\n"
        ".Lopen_cfw_adjust_done:\n"
        "bx lr\n"
    );
}

__attribute__((used, noinline, naked, visibility("default"), pcs("aapcs-vfp")))
open_cfw_state_u32 open_cfw_bootloader_state_range_update_42ced8(void *state)
{
    __asm volatile(
        "push {r4, lr}\n"
        "vpush {d8}\n"
        "movs r4, r0\n"
        "vldr s16, [pc, #528]\n"
        "vldr s0, [r4]\n"
        "vcmp.f32 s0, s16\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bpl .Lopen_cfw_range_not_low\n"
        "vldr s0, [r4]\n"
        "vldr s1, [pc, #512]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "blt .Lopen_cfw_range_not_low\n"
        "movs r0, #0\n"
        "b .Lopen_cfw_range_classified\n"
        ".Lopen_cfw_range_not_low:\n"
        "vldr s0, [r4]\n"
        "vcmp.f32 s0, s16\n"
        "vmrs apsr_nzcv, fpscr\n"
        "blt .Lopen_cfw_range_not_mid\n"
        "vldr s0, [r4]\n"
        "vldr s1, [pc, #480]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bpl .Lopen_cfw_range_not_mid\n"
        "movs r0, #1\n"
        "b .Lopen_cfw_range_classified\n"
        ".Lopen_cfw_range_not_mid:\n"
        "vldr s0, [r4]\n"
        "vldr s1, [pc, #456]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "blt .Lopen_cfw_range_invalid\n"
        "vldr s0, [r4]\n"
        "vldr s1, [pc, #444]\n"
        "vcmp.f32 s0, s1\n"
        "vmrs apsr_nzcv, fpscr\n"
        "bpl .Lopen_cfw_range_invalid\n"
        "movs r0, #2\n"
        "b .Lopen_cfw_range_classified\n"
        ".Lopen_cfw_range_invalid:\n"
        "movs r0, #3\n"
        ".Lopen_cfw_range_classified:\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_range_zero\n"
        "cmp r0, #2\n"
        "beq .Lopen_cfw_range_two\n"
        "blo .Lopen_cfw_range_one\n"
        "b .Lopen_cfw_range_failure\n"
        ".Lopen_cfw_range_zero:\n"
        "ldr.w r0, [pc, #2140]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne .Lopen_cfw_range_zero_call\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #2132]\n"
        "strb r0, [r1]\n"
        ".Lopen_cfw_range_zero_call:\n"
        "movs r0, #0\n"
        "bl open_cfw_bootloader_state_apply_42cea4\n"
        "ldr r0, [pc, #376]\n"
        "str r0, [r4, #4]\n"
        "vstr s16, [r4, #8]\n"
        ".Lopen_cfw_range_success:\n"
        "movs r0, #0\n"
        ".Lopen_cfw_range_return:\n"
        "vpop {d8}\n"
        "pop {r4, pc}\n"
        ".Lopen_cfw_range_one:\n"
        "ldr.w r0, [pc, #2100]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne .Lopen_cfw_range_one_call\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #2092]\n"
        "strb r0, [r1]\n"
        ".Lopen_cfw_range_one_call:\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_state_apply_42cea4\n"
        "ldr.w r0, [pc, #2084]\n"
        "str r0, [r4, #4]\n"
        "ldr r0, [pc, #336]\n"
        "str r0, [r4, #8]\n"
        "b .Lopen_cfw_range_success\n"
        ".Lopen_cfw_range_two:\n"
        "ldr.w r0, [pc, #2064]\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #0\n"
        "bne .Lopen_cfw_range_two_call\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #2056]\n"
        "strb r0, [r1]\n"
        ".Lopen_cfw_range_two_call:\n"
        "movs r0, #2\n"
        "bl open_cfw_bootloader_state_apply_42cea4\n"
        "ldr.w r0, [pc, #2052]\n"
        "str r0, [r4, #4]\n"
        "ldr r0, [pc, #304]\n"
        "str r0, [r4, #8]\n"
        "b .Lopen_cfw_range_success\n"
        ".Lopen_cfw_range_failure:\n"
        "movs r0, #0\n"
        "str r0, [r4, #4]\n"
        "movs r0, #0\n"
        "str r0, [r4, #8]\n"
        "movs r0, #1\n"
        "b .Lopen_cfw_range_return\n"
    );
}

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_state_u32 open_cfw_bootloader_state_event_dispatch_42d562(
    open_cfw_state_u32 event, open_cfw_state_u32 unused,
    open_cfw_state_u8 *state)
{
    __asm volatile(
        "push {r4, lr}\n"
        "movs r4, #0\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq .Lopen_cfw_state_event_zero\n"
        "cmp r0, #2\n"
        "beq .Lopen_cfw_state_event_two\n"
        "blo .Lopen_cfw_state_event_one\n"
        "cmp r0, #4\n"
        "beq .Lopen_cfw_state_event_four\n"
        "blo .Lopen_cfw_state_event_three\n"
        "cmp r0, #6\n"
        "beq .Lopen_cfw_state_event_done\n"
        "blo .Lopen_cfw_state_event_five\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_zero:\n"
        "cmp r2, #0\n"
        "beq .Lopen_cfw_state_event_zero_done\n"
        "ldrb r0, [r2]\n"
        "uxtb r0, r0\n"
        "cmp r0, #2\n"
        "bne .Lopen_cfw_state_event_zero_done\n"
        "bl open_cfw_bootloader_state_event_zero_42cfe0\n"
        ".Lopen_cfw_state_event_zero_done:\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_one:\n"
        "ldrb r0, [r2]\n"
        "movs r1, r0\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "bne .Lopen_cfw_state_event_one_value\n"
        "bl open_cfw_bootloader_state_event_one_zero_42d3bc\n"
        "movs r4, r0\n"
        "b .Lopen_cfw_state_event_join\n"
        ".Lopen_cfw_state_event_one_value:\n"
        "uxtb r0, r0\n"
        "bl open_cfw_bootloader_state_event_one_value_42d104\n"
        "movs r4, r0\n"
        ".Lopen_cfw_state_event_join:\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_two:\n"
        "movs r0, r2\n"
        "bl open_cfw_bootloader_state_range_update_42ced8\n"
        "movs r4, r0\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_three:\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_four:\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_five:\n"
        "b .Lopen_cfw_state_event_done\n"
        ".Lopen_cfw_state_event_done:\n"
        "movs r0, r4\n"
        "pop {r4, pc}\n"
    );
}

#else

typedef struct open_cfw_state_range {
    float sample;
    float lower;
    float upper;
} open_cfw_state_range;

typedef void (*open_cfw_state_apply_fn)(open_cfw_state_u32, void *);
typedef open_cfw_state_u32 (*open_cfw_state_event_fn)(open_cfw_state_u32,
                                                       void *);

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_state_adjust_42cdf8_portable(
    open_cfw_state_u32 state, open_cfw_state_u8 enabled,
    open_cfw_state_u32 mode_register, open_cfw_state_u32 option_register,
    open_cfw_state_u8 option_enabled, open_cfw_state_u32 reference,
    open_cfw_state_u32 *target_register)
{
    open_cfw_state_u32 bias = 0U;
    open_cfw_state_u32 desired;
    open_cfw_state_u32 value;
    if (enabled == 0U || ((mode_register >> 4) & 3U) != 3U) return;
    if (((option_register >> 18) & 1U) != 0U && option_enabled != 0U)
        bias = 15U;
    desired = ((open_cfw_state_u8)state < 2U) ? 10U : 0U;
    if ((int)(desired - bias) >= 1) {
        value = desired - bias;
        value = value < reference ? reference - value : 0U;
    } else {
        value = bias - desired;
        value = value + reference >= 128U ? 127U : value + reference;
    }
    *target_register = (*target_register & ~127U) | (value & 127U);
}

__attribute__((used, noinline, visibility("default")))
open_cfw_state_u32 open_cfw_bootloader_state_range_update_42ced8_portable(
    open_cfw_state_range *state, open_cfw_state_u8 transition_flag,
    open_cfw_state_u8 *range_flag, open_cfw_state_apply_fn apply,
    void *context)
{
    open_cfw_state_u32 range;
    if (state->sample >= -273.0f && state->sample < 35.0f) range = 0U;
    else if (state->sample >= 35.0f && state->sample < 50.0f) range = 1U;
    else if (state->sample >= 50.0f && state->sample < 1000.0f) range = 2U;
    else range = 3U;
    if (range == 3U) {
        state->lower = 0.0f;
        state->upper = 0.0f;
        return 1U;
    }
    if (transition_flag == 0U) *range_flag = range == 2U ? 1U : 0U;
    apply(range, context);
    if (range == 0U) {
        state->lower = -273.0f;
        state->upper = 35.0f;
    } else if (range == 1U) {
        state->lower = 33.0f;
        state->upper = 50.0f;
    } else {
        state->lower = 48.0f;
        state->upper = 1000.0f;
    }
    return 0U;
}

__attribute__((used, noinline, visibility("default")))
open_cfw_state_u32 open_cfw_bootloader_state_event_dispatch_42d562_portable(
    open_cfw_state_u32 event, open_cfw_state_u8 *state,
    open_cfw_state_event_fn event_zero, open_cfw_state_event_fn event_one_zero,
    open_cfw_state_event_fn event_one_value,
    open_cfw_state_u32 (*range_update)(void *, void *), void *context)
{
    if ((open_cfw_state_u8)event == 0U) {
        if (state != (open_cfw_state_u8 *)0 && *state == 2U)
            (void)event_zero(2U, context);
        return 0U;
    }
    if ((open_cfw_state_u8)event == 1U)
        return *state == 0U ? event_one_zero(0U, context)
                            : event_one_value(*state, context);
    if ((open_cfw_state_u8)event == 2U) return range_update(state, context);
    return 0U;
}

#endif
