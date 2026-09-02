/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the Apollo510 SPOT-manager transition_sequence_2b
 * body authenticated at bootloader address 0x00428378.  The target form uses
 * mnemonic Thumb-2 because the 106-byte stock window intentionally shares a
 * distant linker literal table.  The host form expresses the same register
 * transition in portable C for differential tests.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_delay_us_41d1c0(open_cfw_spotmgr_u32 delay_us);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_transition_sequence_2b_428378(void)
{
    /*
     * The PC-relative loads bind the existing authenticated shared literals:
     * 0x428C84 VREFGEN2, 0x428C98 new VDDC trim,
     * 0x428CA0 LDOREG1,   0x428C94 new core-LDO tempco trim,
     * 0x428C90 new core-LDO active trim, 0x428C9C PWRSW0,
     * 0x428BA8 VREFGEN4, 0x428A90 new VDDF trim, and
     * 0x428C88 the ongoing-sequence byte.
     */
    __asm volatile(
        "push {r7, lr}\n"
        "ldr.w r0, [pc, #0x908]\n"
        "ldr.w r1, [pc, #0x918]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #7\n"
        "str r2, [r0]\n"
        "ldr.w r0, [pc, #0x910]\n"
        "ldr.w r1, [pc, #0x900]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #10, #4\n"
        "str r2, [r0]\n"
        "ldr.w r1, [pc, #0x8f0]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #10\n"
        "str r2, [r0]\n"
        "movs r0, #5\n"
        "bl open_cfw_bootloader_delay_us_41d1c0\n"
        "ldr.w r0, [pc, #0x8e8]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x10000\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x2000000\n"
        "str r1, [r0]\n"
        "ldr.w r0, [pc, #0x7e0]\n"
        "ldr.w r1, [pc, #0x6c4]\n"
        "ldr r1, [r1]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #0, #7\n"
        "str r2, [r0]\n"
        "movs r0, #26\n"
        "ldr.w r1, [pc, #0x8ac]\n"
        "strb r0, [r1]\n"
        "pop {r0, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_transition_state {
    open_cfw_spotmgr_u32 vrefgen2;
    open_cfw_spotmgr_u32 ldoreg1;
    open_cfw_spotmgr_u32 pwrsw0;
    open_cfw_spotmgr_u32 vrefgen4;
    open_cfw_spotmgr_u32 new_vddc_trim;
    open_cfw_spotmgr_u32 new_coreldo_tempco_trim;
    open_cfw_spotmgr_u32 new_coreldo_active_trim;
    open_cfw_spotmgr_u32 new_vddf_trim;
    open_cfw_spotmgr_u8 ongoing_sequence;
    open_cfw_spotmgr_u32 delay_calls;
    open_cfw_spotmgr_u32 last_delay_us;
} open_cfw_spotmgr_transition_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_transition_sequence_2b_428378(
    open_cfw_spotmgr_transition_state *state)
{
    state->vrefgen2 =
        (state->vrefgen2 & ~0x7fU) | (state->new_vddc_trim & 0x7fU);
    state->ldoreg1 = (state->ldoreg1 & ~(0xfU << 10)) |
        ((state->new_coreldo_tempco_trim & 0xfU) << 10);
    state->ldoreg1 = (state->ldoreg1 & ~0x3ffU) |
        (state->new_coreldo_active_trim & 0x3ffU);
    state->delay_calls += 1U;
    state->last_delay_us = 5U;
    state->pwrsw0 &= ~(1U << 16);
    state->pwrsw0 &= ~(1U << 25);
    state->vrefgen4 =
        (state->vrefgen4 & ~0x7fU) | (state->new_vddf_trim & 0x7fU);
    state->ongoing_sequence = 26U;
}

#endif
