/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable Apollo510 SPOT-manager power-transition trim transaction
 * authenticated at G2 bootloader address 0x0042B06C.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_pt_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_pt_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_delay_cycles_41d1c0(open_cfw_spotmgr_pt_u32);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_power_transition_trims_42b06c(
    open_cfw_spotmgr_pt_u32 power_state __attribute__((unused)),
    open_cfw_spotmgr_pt_u32 transition __attribute__((unused)))
{
    __asm volatile(
        "push.w {r4, r5, r6, r7, r8, r9, r10, lr}\n"
        "mov r10, r0\n"
        "movs r5, r1\n"
        "ldr.w r6, [pc, #0x630]\n"
        "ldr r0, [r6]\n"
        "lsls r0, r0, #22\n"
        "lsrs r0, r0, #22\n"
        "adds r0, #14\n"
        "cmp.w r0, #0x400\n"
        "blo.n .Lpt_core_delta_regular\n"
        "movw r7, #0x3ff\n"
        "ldr r0, [r6]\n"
        "lsls r0, r0, #22\n"
        "lsrs r0, r0, #22\n"
        "subs r7, r7, r0\n"
        "b.n .Lpt_core_delta_ready\n"
        ".Lpt_core_delta_regular:\n"
        "movs r7, #14\n"
        ".Lpt_core_delta_ready:\n"
        "ldr.w r8, [pc, #0x608]\n"
        "ldr.w r0, [r8]\n"
        "ands r0, r0, #0x3f\n"
        "adds r0, r0, #6\n"
        "cmp r0, #0x40\n"
        "blo.n .Lpt_flash_delta_regular\n"
        "ldr.w r9, [r8]\n"
        "ands r9, r9, #0x3f\n"
        "rsbs.w r9, r9, #0x3f\n"
        "b.n .Lpt_flash_delta_ready\n"
        ".Lpt_flash_delta_regular:\n"
        "movs.w r9, #6\n"
        ".Lpt_flash_delta_ready:\n"
        "ldr r0, [r6]\n"
        "lsrs r1, r0, #10\n"
        "lsls r1, r1, #10\n"
        "adds r0, r7, r0\n"
        "lsls r0, r0, #22\n"
        "lsrs r0, r0, #22\n"
        "orrs r0, r1\n"
        "str r0, [r6]\n"
        "ldr.w r0, [r8]\n"
        "lsrs r1, r0, #6\n"
        "lsls r1, r1, #6\n"
        "adds.w r0, r9, r0\n"
        "ands r0, r0, #0x3f\n"
        "orrs r0, r1\n"
        "str.w r0, [r8]\n"
        "movs r0, #20\n"
        "bl open_cfw_bootloader_delay_cycles_41d1c0\n"
        "ldr.w r4, [pc, #0x904]\n"
        "ldr r0, [r4]\n"
        "orrs r0, r0, #0x20000000\n"
        "str r0, [r4]\n"
        "ldr r0, [r4]\n"
        "orrs r0, r0, #0x10000000\n"
        "str r0, [r4]\n"
        "movs r0, #20\n"
        "bl open_cfw_bootloader_delay_cycles_41d1c0\n"
        "cmp.w r10, #0\n"
        "beq.n .Lpt_state0\n"
        "cmp.w r10, #2\n"
        "beq.n .Lpt_state2\n"
        "blo.n .Lpt_state1\n"
        "cmp.w r10, #4\n"
        "beq.n .Lpt_state4\n"
        "blo.n .Lpt_state3\n"
        "cmp.w r10, #6\n"
        "beq.n .Lpt_state6\n"
        "blo.n .Lpt_state5\n"
        "cmp.w r10, #7\n"
        "beq.n .Lpt_state7\n"
        "b.n .Lpt_state_default\n"
        ".Lpt_state0:\n"
        "ldr.w r1, [pc, #0x57c]\n"
        "ldrb.w r0, [r1, #0x5c]\n"
        "ands r0, r0, #0x1f\n"
        "ldr r1, [r1, #0x5c]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state1:\n"
        "ldr.w r1, [pc, #0x568]\n"
        "ldr r0, [r1, #0x5c]\n"
        "ubfx r0, r0, #5, #5\n"
        "ldr r1, [r1, #0x5c]\n"
        "ubfx r1, r1, #15, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state2:\n"
        "ldr.w r1, [pc, #0x554]\n"
        "ldrb.w r0, [r1, #0x54]\n"
        "ands r0, r0, #0x1f\n"
        "ldrb.w r1, [r1, #0x58]\n"
        "ands r1, r1, #0x1f\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state3:\n"
        "ldr.w r1, [pc, #0x540]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #10, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state4:\n"
        "ldr.w r1, [pc, #0x52c]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #5, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #5, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state5:\n"
        "ldr.w r1, [pc, #0x51c]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #15, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #15, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state6:\n"
        "ldr.w r1, [pc, #0x508]\n"
        "ldrb.w r0, [r1, #0x60]\n"
        "ands r0, r0, #0x1f\n"
        "ldr r1, [r1, #0x60]\n"
        "ubfx r1, r1, #10, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state7:\n"
        "ldr.w r0, [pc, #0x840]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #11, #5\n"
        "ldr.w r1, [pc, #0x83c]\n"
        "ldr r1, [r1]\n"
        "ubfx r1, r1, #17, #5\n"
        "b.n .Lpt_state_ready\n"
        ".Lpt_state_default:\n"
        "ldr.w r1, [pc, #0x4e0]\n"
        "ldr r0, [r1, #0x54]\n"
        "ubfx r0, r0, #15, #5\n"
        "ldr r1, [r1, #0x58]\n"
        "ubfx r1, r1, #15, #5\n"
        ".Lpt_state_ready:\n"
        "cmp r5, #8\n"
        "bne.n .Lpt_transition12\n"
        "ldr.w r0, [pc, #0x4cc]\n"
        "ldr r0, [r0, #0x5c]\n"
        "ubfx r0, r0, #20, #5\n"
        "b.n .Lpt_transition_ready\n"
        ".Lpt_transition12:\n"
        "cmp r5, #12\n"
        "bne.n .Lpt_transition14\n"
        "ldr.w r0, [pc, #0x4bc]\n"
        "ldr r0, [r0, #0x54]\n"
        "ubfx r0, r0, #20, #5\n"
        "b.n .Lpt_transition_ready\n"
        ".Lpt_transition14:\n"
        "cmp r5, #14\n"
        "bne.n .Lpt_transition15\n"
        "adds r2, r0, #6\n"
        "cmp r2, #0x20\n"
        "blo.n .Lpt_add6\n"
        "movs r0, #0x1f\n"
        "b.n .Lpt_transition_ready\n"
        ".Lpt_add6:\n"
        "adds r0, r0, #6\n"
        "b.n .Lpt_transition_ready\n"
        ".Lpt_transition15:\n"
        "cmp r5, #15\n"
        "bne.n .Lpt_transition_ready\n"
        "adds.w r2, r0, #12\n"
        "cmp r2, #0x20\n"
        "blo.n .Lpt_add12\n"
        "movs r0, #0x1f\n"
        "b.n .Lpt_transition_ready\n"
        ".Lpt_add12:\n"
        "adds r0, #12\n"
        ".Lpt_transition_ready:\n"
        "ldr.w r2, [pc, #0x7d8]\n"
        "ldr r3, [r2]\n"
        "bfi r3, r0, #25, #5\n"
        "str r3, [r2]\n"
        "ldr.w r0, [pc, #0x7d4]\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #8, #5\n"
        "str r2, [r0]\n"
        "cmp r5, #1\n"
        "beq.n .Lpt_low_power_value\n"
        "cmp r5, #5\n"
        "beq.n .Lpt_low_power_value\n"
        "cmp r5, #17\n"
        "bne.n .Lpt_normal_value\n"
        ".Lpt_low_power_value:\n"
        "ldr.w r0, [pc, #0xba8]\n"
        "movs r1, #4\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #25, #5\n"
        "str r2, [r0]\n"
        "b.n .Lpt_restore\n"
        ".Lpt_normal_value:\n"
        "ldr.w r0, [pc, #0xb98]\n"
        "movs r1, #6\n"
        "ldr r2, [r0]\n"
        "bfi r2, r1, #25, #5\n"
        "str r2, [r0]\n"
        ".Lpt_restore:\n"
        "ldr r0, [r4]\n"
        "bics r0, r0, #0x20000000\n"
        "str r0, [r4]\n"
        "ldr r0, [r4]\n"
        "bics r0, r0, #0x10000000\n"
        "str r0, [r4]\n"
        "ldr r0, [r6]\n"
        "lsrs r1, r0, #10\n"
        "lsls r1, r1, #10\n"
        "subs r7, r0, r7\n"
        "lsls r7, r7, #22\n"
        "lsrs r7, r7, #22\n"
        "orrs r7, r1\n"
        "str r7, [r6]\n"
        "ldr.w r0, [r8]\n"
        "lsrs r1, r0, #6\n"
        "lsls r1, r1, #6\n"
        "subs.w r9, r0, r9\n"
        "ands r9, r9, #0x3f\n"
        "orrs.w r9, r9, r1\n"
        "str.w r9, [r8]\n"
        "pop.w {r4, r5, r6, r7, r8, r9, r10, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_pt_state {
    open_cfw_spotmgr_pt_u32 core_trim;
    open_cfw_spotmgr_pt_u32 flash_trim;
    open_cfw_spotmgr_pt_u32 transition_control;
    open_cfw_spotmgr_pt_u32 profile_54;
    open_cfw_spotmgr_pt_u32 profile_58;
    open_cfw_spotmgr_pt_u32 profile_5c;
    open_cfw_spotmgr_pt_u32 profile_60;
    open_cfw_spotmgr_pt_u32 state7_core;
    open_cfw_spotmgr_pt_u32 state7_flash;
    open_cfw_spotmgr_pt_u32 simobuck_core;
    open_cfw_spotmgr_pt_u32 simobuck_flash;
    open_cfw_spotmgr_pt_u32 mode_trim;
    open_cfw_spotmgr_pt_u32 delay_calls;
} open_cfw_spotmgr_pt_state;

static open_cfw_spotmgr_pt_u32 open_cfw_spotmgr_pt_field(
    open_cfw_spotmgr_pt_u32 value, open_cfw_spotmgr_pt_u32 shift)
{
    return (value >> shift) & 0x1fU;
}

static open_cfw_spotmgr_pt_u32 open_cfw_spotmgr_pt_insert(
    open_cfw_spotmgr_pt_u32 value, open_cfw_spotmgr_pt_u32 field,
    open_cfw_spotmgr_pt_u32 shift)
{
    return (value & ~(0x1fU << shift)) | ((field & 0x1fU) << shift);
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_power_transition_trims_42b06c(
    open_cfw_spotmgr_pt_u32 power_state,
    open_cfw_spotmgr_pt_u32 transition,
    open_cfw_spotmgr_pt_state *state)
{
    open_cfw_spotmgr_pt_u32 core_delta = 14U;
    open_cfw_spotmgr_pt_u32 flash_delta = 6U;
    open_cfw_spotmgr_pt_u32 core = state->core_trim & 0x3ffU;
    open_cfw_spotmgr_pt_u32 flash = state->flash_trim & 0x3fU;
    open_cfw_spotmgr_pt_u32 core_code;
    open_cfw_spotmgr_pt_u32 flash_code;

    if (core + core_delta >= 0x400U) {
        core_delta = 0x3ffU - core;
    }
    if (flash + flash_delta >= 0x40U) {
        flash_delta = 0x3fU - flash;
    }
    state->core_trim = (state->core_trim & ~0x3ffU) |
        ((core + core_delta) & 0x3ffU);
    state->flash_trim = (state->flash_trim & ~0x3fU) |
        ((flash + flash_delta) & 0x3fU);
    state->delay_calls += 1U;
    state->transition_control |= 0x30000000U;
    state->delay_calls += 1U;

    switch (power_state) {
    case 0U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_5c, 0U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_5c, 10U);
        break;
    case 1U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_5c, 5U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_5c, 15U);
        break;
    case 2U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_54, 0U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_58, 0U);
        break;
    case 3U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_54, 10U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_58, 10U);
        break;
    case 4U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_54, 5U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_58, 5U);
        break;
    case 6U:
        core_code = open_cfw_spotmgr_pt_field(state->profile_60, 0U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_60, 10U);
        break;
    case 7U:
        core_code = open_cfw_spotmgr_pt_field(state->state7_core, 11U);
        flash_code = open_cfw_spotmgr_pt_field(state->state7_flash, 17U);
        break;
    default:
        core_code = open_cfw_spotmgr_pt_field(state->profile_54, 15U);
        flash_code = open_cfw_spotmgr_pt_field(state->profile_58, 15U);
        break;
    }

    if (transition == 8U) {
        core_code = open_cfw_spotmgr_pt_field(state->profile_5c, 20U);
    } else if (transition == 12U) {
        core_code = open_cfw_spotmgr_pt_field(state->profile_54, 20U);
    } else if (transition == 14U) {
        core_code = core_code + 6U < 32U ? core_code + 6U : 31U;
    } else if (transition == 15U) {
        core_code = core_code + 12U < 32U ? core_code + 12U : 31U;
    }

    state->simobuck_core = open_cfw_spotmgr_pt_insert(
        state->simobuck_core, core_code, 25U);
    state->simobuck_flash = open_cfw_spotmgr_pt_insert(
        state->simobuck_flash, flash_code, 8U);
    state->mode_trim = open_cfw_spotmgr_pt_insert(
        state->mode_trim,
        (transition == 1U || transition == 5U || transition == 17U) ? 4U : 6U,
        25U);
    state->transition_control &= ~0x30000000U;
    state->core_trim = (state->core_trim & ~0x3ffU) | core;
    state->flash_trim = (state->flash_trim & ~0x3fU) | flash;
}

#endif
