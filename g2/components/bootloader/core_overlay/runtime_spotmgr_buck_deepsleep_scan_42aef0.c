/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the second Apollo510 SPOT-manager SIMOBUCK
 * deep-sleep eligibility scan authenticated at G2 bootloader address
 * 0x0042AEF0.  The target form preserves the fixed instruction layout;
 * the portable form exposes the predicate for deterministic host tests.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_scan_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_scan_u8;

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_spotmgr_scan_u32
open_cfw_bootloader_stimer_is_running_41f3f0(void);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0(
    const void *power_status __attribute__((unused)))
{
    __asm volatile(
        "push {r7, lr}\n"
        "ldrb r1, [r0, #16]\n"
        "cmp r1, #3\n"
        "beq.n .Lspot_scan_force\n"
        "ldr r1, [r0]\n"
        "lsls r1, r1, #2\n"
        "bne.n .Lspot_scan_force\n"
        "ldr r0, [r0, #4]\n"
        "movw r1, #0x4c4\n"
        "tst r0, r1\n"
        "bne.n .Lspot_scan_force\n"
        "ldr.w r0, [pc, #0xac8]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #29, #1\n"
        "cmp r0, #0\n"
        "beq.n .Lspot_scan_check_stimer\n"
        ".Lspot_scan_force:\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xabc]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_scan_return\n"
        ".Lspot_scan_check_stimer:\n"
        "bl open_cfw_bootloader_stimer_is_running_41f3f0\n"
        "cmp r0, #0\n"
        "beq.n .Lspot_scan_timer_begin\n"
        "ldr.w r0, [pc, #0xab0]\n"
        "ldr r1, [r0]\n"
        "ands r1, r1, #15\n"
        "cmp r1, #1\n"
        "blt.n .Lspot_scan_timer_begin\n"
        "ldr r0, [r0]\n"
        "ands r0, r0, #15\n"
        "cmp r0, #3\n"
        "bge.n .Lspot_scan_timer_begin\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xa94]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_scan_return\n"
        ".Lspot_scan_timer_begin:\n"
        "movs r0, #0\n"
        "b.n .Lspot_scan_timer_test\n"
        ".Lspot_scan_timer_next:\n"
        "adds r0, r0, #1\n"
        ".Lspot_scan_timer_test:\n"
        "cmp r0, #16\n"
        "bhs.n .Lspot_scan_clear\n"
        "ldr.w r1, [pc, #0xa88]\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "lsls r2, r2, #31\n"
        "bpl.n .Lspot_scan_timer_inactive\n"
        "ldr.w r2, [pc, #0xa7c]\n"
        "ldr r2, [r2]\n"
        "lsrs r2, r0\n"
        "lsls r2, r2, #31\n"
        "bpl.n .Lspot_scan_timer_inactive\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #0\n"
        "bmi.n .Lspot_scan_clock_after_low\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #6\n"
        "blt.n .Lspot_scan_clock_match\n"
        ".Lspot_scan_clock_after_low:\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #19\n"
        "blt.n .Lspot_scan_clock_mid_no\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #25\n"
        "bge.n .Lspot_scan_clock_mid_no\n"
        "movs r2, #1\n"
        "b.n .Lspot_scan_clock_mid_done\n"
        ".Lspot_scan_clock_mid_no:\n"
        "movs r2, #0\n"
        ".Lspot_scan_clock_mid_done:\n"
        "uxtb r2, r2\n"
        "cmp r2, #0\n"
        "bne.n .Lspot_scan_clock_match\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp.w r2, #0x100\n"
        "blt.n .Lspot_scan_clock_gpio_no\n"
        "adds.w r1, r1, r0, lsl #5\n"
        "ldr.w r1, [r1, #0x200]\n"
        "ubfx r1, r1, #8, #9\n"
        "cmp.w r1, #0x1e0\n"
        "bge.n .Lspot_scan_clock_gpio_no\n"
        "movs r1, #1\n"
        "b.n .Lspot_scan_clock_gpio_done\n"
        ".Lspot_scan_clock_gpio_no:\n"
        "movs r1, #0\n"
        ".Lspot_scan_clock_gpio_done:\n"
        "eors r1, r1, #1\n"
        "b.n .Lspot_scan_clock_match_fold\n"
        ".Lspot_scan_clock_match:\n"
        "movs r1, #0\n"
        ".Lspot_scan_clock_match_fold:\n"
        "eors r1, r1, #1\n"
        "b.n .Lspot_scan_clock_ready\n"
        ".Lspot_scan_timer_inactive:\n"
        "movs r1, #0\n"
        ".Lspot_scan_clock_ready:\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq.n .Lspot_scan_timer_next\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0x9d8]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_scan_return\n"
        ".Lspot_scan_clear:\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0x9cc]\n"
        "strb r0, [r1]\n"
        ".Lspot_scan_return:\n"
        "pop {r0, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_scan_state {
    open_cfw_spotmgr_scan_u32 dev_power_status;
    open_cfw_spotmgr_scan_u32 audss_power_status;
    open_cfw_spotmgr_scan_u8 reserved_08[8];
    open_cfw_spotmgr_scan_u8 temperature_range;
    open_cfw_spotmgr_scan_u8 syspll_enabled;
    open_cfw_spotmgr_scan_u8 stimer_running;
    open_cfw_spotmgr_scan_u8 stimer_clock;
    open_cfw_spotmgr_scan_u32 timer_ctrl[16];
    open_cfw_spotmgr_scan_u32 timer_global_enable;
    open_cfw_spotmgr_scan_u8 deep_sleep_blocked;
} open_cfw_spotmgr_scan_state;

static open_cfw_spotmgr_scan_u32 open_cfw_spotmgr_scan_clock_matches(
    open_cfw_spotmgr_scan_u32 clock)
{
    return (clock < 6U) || ((clock >= 19U) && (clock < 25U)) ||
        ((clock >= 0x100U) && (clock < 0x1e0U));
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0(
    open_cfw_spotmgr_scan_state *state)
{
    open_cfw_spotmgr_scan_u32 index;

    if ((state->temperature_range == 3U) ||
        ((state->dev_power_status & 0x3fffffffU) != 0U) ||
        ((state->audss_power_status & 0x4c4U) != 0U) ||
        (state->syspll_enabled != 0U)) {
        state->deep_sleep_blocked = 1U;
        return;
    }

    if ((state->stimer_running != 0U) &&
        (state->stimer_clock >= 1U) && (state->stimer_clock < 3U)) {
        state->deep_sleep_blocked = 1U;
        return;
    }

    for (index = 0U; index < 16U; ++index) {
        open_cfw_spotmgr_scan_u32 control = state->timer_ctrl[index];
        if (((control & 1U) != 0U) &&
            ((state->timer_global_enable & (1U << index)) != 0U) &&
            open_cfw_spotmgr_scan_clock_matches((control >> 8) & 0x1ffU)) {
            state->deep_sleep_blocked = 1U;
            return;
        }
    }
    state->deep_sleep_blocked = 0U;
}

#endif
