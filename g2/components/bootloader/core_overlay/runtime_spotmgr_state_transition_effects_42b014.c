/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the Apollo510 SPOT-manager state-transition
 * side-effect leaf authenticated at G2 bootloader address 0x0042B014.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_effect_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_effect_u8;

#if defined(__arm__) || defined(__thumb__)

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_state_transition_effects_42b014(
    open_cfw_spotmgr_effect_u32 prior_state __attribute__((unused)),
    open_cfw_spotmgr_effect_u32 next_state __attribute__((unused)))
{
    __asm volatile(
        "movs r2, r1\n"
        "uxtb r2, r2\n"
        "cmp r2, #1\n"
        "bne.n .Lspot_effect_check_hp\n"
        "movs r2, r0\n"
        "uxtb r2, r2\n"
        "cmp r2, #2\n"
        "bne.n .Lspot_effect_check_hp\n"
        "ldr.w r2, [pc, #0x9a0]\n"
        "ldrb r2, [r2]\n"
        "cmp r2, #0\n"
        "bne.n .Lspot_effect_check_hp\n"
        "movs r2, #1\n"
        "ldr.w r3, [pc, #0x9b4]\n"
        "strb r2, [r3]\n"
        ".Lspot_effect_check_hp:\n"
        "uxtb r1, r1\n"
        "cmp r1, #1\n"
        "bne.n .Lspot_effect_return\n"
        "uxtb r0, r0\n"
        "cmp r0, #0\n"
        "bne.n .Lspot_effect_return\n"
        "ldr.w r0, [pc, #0x98c]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x10000\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #8\n"
        "str r1, [r0]\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x40\n"
        "str r1, [r0]\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x964]\n"
        "strb r0, [r1]\n"
        ".Lspot_effect_return:\n"
        "bx lr\n"
    );
}

#else

typedef struct open_cfw_spotmgr_effect_state {
    open_cfw_spotmgr_effect_u8 hp_entry_pending;
    open_cfw_spotmgr_effect_u8 deep_sleep_entry_pending;
    open_cfw_spotmgr_effect_u32 power_control;
} open_cfw_spotmgr_effect_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_state_transition_effects_42b014(
    open_cfw_spotmgr_effect_u32 prior_state,
    open_cfw_spotmgr_effect_u32 next_state,
    open_cfw_spotmgr_effect_state *state)
{
    if (((open_cfw_spotmgr_effect_u8)next_state == 1U) &&
        ((open_cfw_spotmgr_effect_u8)prior_state == 2U) &&
        (state->hp_entry_pending == 0U)) {
        state->deep_sleep_entry_pending = 1U;
    }
    if (((open_cfw_spotmgr_effect_u8)next_state == 1U) &&
        ((open_cfw_spotmgr_effect_u8)prior_state == 0U)) {
        state->power_control &= ~(0x10000U | 0x08U | 0x40U);
        state->hp_entry_pending = 0U;
    }
}

#endif
