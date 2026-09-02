/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the Apollo510 SPOT-manager transition_sequence_7b
 * body authenticated at bootloader address 0x00428A94. The target form uses
 * mnemonic Thumb-2 because the fixed 276-byte body shares linker literals
 * outside its own interval. The host form exposes the same bounded state
 * transition for deterministic differential tests.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr7b_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr7b_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_delay_us_41d1c0(
    open_cfw_spotmgr7b_u32 delay_us);
extern void open_cfw_bootloader_delay_us_status_change_41d21c(
    open_cfw_spotmgr7b_u32 delay_us,
    volatile open_cfw_spotmgr7b_u32 *status,
    open_cfw_spotmgr7b_u32 mask,
    open_cfw_spotmgr7b_u32 expected);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94(void)
{
    /*
     * Authenticated shared literals bind VREFGEN2/new-VDDC, LDOREG1/core-LDO
     * trims, VREFGEN4/new-VDDF, PWRCTRL, PWRSW0, CLKGEN MISC/CLOCKENSTAT,
     * and the ongoing-sequence byte without adding target data.
     */
    __asm volatile(
        "push {r3, r4, r5, r6, r7, lr}\n"
        "movs r0, #1\n"
        "ldr r0, [pc, #0x1e8]\n"
        "ldr r1, [pc, #0x1fc]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #7\n"
        "str r2, [r0]\n"
        "ldr r0, [pc, #0x1f8]\n"
        "ldr r1, [pc, #0x1e8]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #10, #4\n"
        "str r2, [r0]\n"
        "ldr r1, [pc, #0x1d8]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #10\n"
        "str r2, [r0]\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\n"
        "ldr r0, [pc, #0xe0]\n"
        "ldr.w r1, [pc, #0xa54]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #7\n"
        "str r2, [r0]\n"
        "ldr.w r4, [pc, #0x708]\n"
        "ldr r0, [r4]\n"
        "ands r0, r0, #3\n"
        "cmp r0, #2\n"
        "beq.n .Lspot7b_was_hp\n"
        "movs r0, #0\n"
        "b.n .Lspot7b_power_switches\n"
        ".Lspot7b_was_hp:\n"
        "movs r0, #1\n"
        "ldr r1, [r4]\n"
        "bfi r1, r0, #0, #2\n"
        "str r1, [r4]\n"
        "movs r5, #0\n"
        "b.n .Lspot7b_lp_poll_test\n"
        ".Lspot7b_lp_poll_delay:\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\n"
        "adds r5, r5, #1\n"
        ".Lspot7b_lp_poll_test:\n"
        "cmp r5, #20\n"
        "bhs.n .Lspot7b_lp_poll_done\n"
        "ldr r0, [r4]\n"
        "ubfx r0, r0, #2, #1\n"
        "cmp r0, #1\n"
        "blt.n .Lspot7b_lp_poll_delay\n"
        ".Lspot7b_lp_poll_done:\n"
        "movs r0, #1\n"
        ".Lspot7b_power_switches:\n"
        "ldr r1, [pc, #0x18c]\n"
        "ldr r2, [r1]\n"
        "orrs r2, r2, #0x40\n"
        "str r2, [r1]\n"
        "ldr r2, [r1]\n"
        "orrs r2, r2, #8\n"
        "str r2, [r1]\n"
        "ldr r2, [r1]\n"
        "bics r2, r2, #0x2000000\n"
        "str r2, [r1]\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "beq.n .Lspot7b_finish\n"
        "movs r6, #0\n"
        "ldr.w r5, [pc, #0x6b0]\n"
        "ldr r0, [r5]\n"
        "ubfx r0, r0, #5, #1\n"
        "cmp r0, #0\n"
        "bne.n .Lspot7b_hfrc2_ready_test\n"
        "ldr r0, [r5]\n"
        "orrs r0, r0, #0x20\n"
        "str r0, [r5]\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\n"
        "movs.w r3, #0x1000000\n"
        "movs.w r2, #0x1000000\n"
        "ldr.w r1, [pc, #0x690]\n"
        "movs r0, #15\n"
        "bl open_cfw_bootloader_delay_us_status_change_41d21c\n"
        "movs r6, #1\n"
        ".Lspot7b_hfrc2_ready_test:\n"
        "ldr.w r0, [pc, #0x684]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #24, #1\n"
        "cmp r0, #0\n"
        "beq.n .Lspot7b_clear_force_test\n"
        "movs r0, #2\n"
        "ldr r1, [r4]\n"
        "bfi r1, r0, #0, #2\n"
        "str r1, [r4]\n"
        "movs r7, #0\n"
        "b.n .Lspot7b_hp_poll_test\n"
        ".Lspot7b_hp_poll_delay:\n"
        "movs r0, #1\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\n"
        "adds r7, r7, #1\n"
        ".Lspot7b_hp_poll_test:\n"
        "cmp r7, #20\n"
        "bhs.n .Lspot7b_clear_force_test\n"
        "ldr r0, [r4]\n"
        "ubfx r0, r0, #2, #1\n"
        "cmp r0, #1\n"
        "blt.n .Lspot7b_hp_poll_delay\n"
        ".Lspot7b_clear_force_test:\n"
        "uxtb r6, r6\n"
        "cmp r6, #0\n"
        "beq.n .Lspot7b_finish\n"
        "ldr r0, [r5]\n"
        "bics r0, r0, #0x20\n"
        "str r0, [r5]\n"
        ".Lspot7b_finish:\n"
        "movs r0, #26\n"
        "ldr r1, [pc, #0xe4]\n"
        "strb r0, [r1]\n"
        "pop {r0, r4, r5, r6, r7, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_transition_7b_state {
    open_cfw_spotmgr7b_u32 vrefgen2;
    open_cfw_spotmgr7b_u32 ldoreg1;
    open_cfw_spotmgr7b_u32 vrefgen4;
    open_cfw_spotmgr7b_u32 mcuperfreq;
    open_cfw_spotmgr7b_u32 pwrsw0;
    open_cfw_spotmgr7b_u32 clkgen_misc;
    open_cfw_spotmgr7b_u32 clkgen_clockenstat;
    open_cfw_spotmgr7b_u32 new_vddc_trim;
    open_cfw_spotmgr7b_u32 new_coreldo_tempco_trim;
    open_cfw_spotmgr7b_u32 new_coreldo_active_trim;
    open_cfw_spotmgr7b_u32 new_vddf_trim;
    open_cfw_spotmgr7b_u8 ongoing_sequence;
    open_cfw_spotmgr7b_u32 delay_calls;
    open_cfw_spotmgr7b_u32 one_us_delay_calls;
    open_cfw_spotmgr7b_u32 last_delay_us;
    open_cfw_spotmgr7b_u32 status_change_calls;
    open_cfw_spotmgr7b_u32 last_status_delay;
    open_cfw_spotmgr7b_u32 last_status_mask;
    open_cfw_spotmgr7b_u32 last_status_expected;
} open_cfw_spotmgr_transition_7b_state;

static void open_cfw_spotmgr7b_delay(
    open_cfw_spotmgr_transition_7b_state *state,
    open_cfw_spotmgr7b_u32 delay_us)
{
    state->delay_calls += 1U;
    state->last_delay_us = delay_us;
    if (delay_us == 1U) {
        state->one_us_delay_calls += 1U;
    }
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94(
    open_cfw_spotmgr_transition_7b_state *state)
{
    open_cfw_spotmgr7b_u32 switch_back_to_hp;
    open_cfw_spotmgr7b_u32 forced_hfrc2 = 0U;
    open_cfw_spotmgr7b_u32 index;

    state->vrefgen2 =
        (state->vrefgen2 & ~0x7fU) | (state->new_vddc_trim & 0x7fU);
    state->ldoreg1 = (state->ldoreg1 & ~(0xfU << 10)) |
        ((state->new_coreldo_tempco_trim & 0xfU) << 10);
    state->ldoreg1 = (state->ldoreg1 & ~0x3ffU) |
        (state->new_coreldo_active_trim & 0x3ffU);
    open_cfw_spotmgr7b_delay(state, 5U);
    state->vrefgen4 =
        (state->vrefgen4 & ~0x7fU) | (state->new_vddf_trim & 0x7fU);

    switch_back_to_hp = ((state->mcuperfreq & 3U) == 2U) ? 1U : 0U;
    if (switch_back_to_hp != 0U) {
        state->mcuperfreq = (state->mcuperfreq & ~3U) | 1U;
        for (index = 0U; index < 20U; ++index) {
            if (((state->mcuperfreq >> 2) & 1U) >= 1U) {
                break;
            }
            open_cfw_spotmgr7b_delay(state, 1U);
        }
    }

    state->pwrsw0 |= 1U << 6;
    state->pwrsw0 |= 1U << 3;
    state->pwrsw0 &= ~(1U << 25);

    if (switch_back_to_hp != 0U) {
        if (((state->clkgen_misc >> 5) & 1U) == 0U) {
            state->clkgen_misc |= 1U << 5;
            open_cfw_spotmgr7b_delay(state, 1U);
            state->status_change_calls += 1U;
            state->last_status_delay = 15U;
            state->last_status_mask = 1U << 24;
            state->last_status_expected = 1U << 24;
            forced_hfrc2 = 1U;
        }
        if (((state->clkgen_clockenstat >> 24) & 1U) != 0U) {
            state->mcuperfreq = (state->mcuperfreq & ~3U) | 2U;
            for (index = 0U; index < 20U; ++index) {
                if (((state->mcuperfreq >> 2) & 1U) >= 1U) {
                    break;
                }
                open_cfw_spotmgr7b_delay(state, 1U);
            }
        }
        if (forced_hfrc2 != 0U) {
            state->clkgen_misc &= ~(1U << 5);
        }
    }
    state->ongoing_sequence = 26U;
}

#endif
