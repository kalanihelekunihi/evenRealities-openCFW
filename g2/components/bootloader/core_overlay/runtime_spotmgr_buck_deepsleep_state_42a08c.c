/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the Apollo510 SPOT-manager SIMOBUCK deep-sleep
 * state classifier authenticated at G2 bootloader address 0x0042A08C.
 * The target form preserves the fixed instruction and shared-literal layout;
 * the portable form exposes the same predicate for deterministic host tests.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_buck_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_buck_u8;

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_spotmgr_buck_u32
open_cfw_bootloader_stimer_is_running_41f3f0(void);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c(
    const void *power_status __attribute__((unused)))
{
    __asm volatile(
        "push {r7, lr}\n"
        "ldrb r1, [r0, #16]\n"
        "cmp r1, #3\n"
        "beq.n .Lspot_buck_force\n"
        "ldr r1, [r0]\n"
        "lsls r1, r1, #2\n"
        "bne.n .Lspot_buck_force\n"
        "ldr r0, [r0, #4]\n"
        "movw r1, #0x4c4\n"
        "tst r0, r1\n"
        "bne.n .Lspot_buck_force\n"
        "ldr.w r0, [pc, #0x7cc]\n"
        "ldr r0, [r0]\n"
        "ubfx r0, r0, #29, #1\n"
        "cmp r0, #0\n"
        "beq.n .Lspot_buck_check_stimer\n"
        ".Lspot_buck_force:\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xb00]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_buck_return\n"
        ".Lspot_buck_check_stimer:\n"
        "bl open_cfw_bootloader_stimer_is_running_41f3f0\n"
        "cmp r0, #0\n"
        "beq.n .Lspot_buck_timer_begin\n"
        "ldr.w r0, [pc, #0xaa8]\n"
        "ldr r1, [r0]\n"
        "ands r1, r1, #15\n"
        "cmp r1, #1\n"
        "blt.n .Lspot_buck_timer_begin\n"
        "ldr r0, [r0]\n"
        "ands r0, r0, #15\n"
        "cmp r0, #3\n"
        "bge.n .Lspot_buck_timer_begin\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xad8]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_buck_return\n"
        ".Lspot_buck_timer_begin:\n"
        "movs r0, #0\n"
        "b.n .Lspot_buck_timer_test\n"
        ".Lspot_buck_timer_next:\n"
        "adds r0, r0, #1\n"
        ".Lspot_buck_timer_test:\n"
        "cmp r0, #16\n"
        "bhs.n .Lspot_buck_clear\n"
        "ldr.w r1, [pc, #0xa80]\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "lsls r2, r2, #31\n"
        "bpl.n .Lspot_buck_timer_inactive\n"
        "ldr.w r2, [pc, #0xa74]\n"
        "ldr r2, [r2]\n"
        "lsrs r2, r0\n"
        "lsls r2, r2, #31\n"
        "bpl.n .Lspot_buck_timer_inactive\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #6\n"
        "blt.n .Lspot_buck_clock_match\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #19\n"
        "blt.n .Lspot_buck_clock_mid_no\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp r2, #25\n"
        "bge.n .Lspot_buck_clock_mid_no\n"
        "movs r2, #1\n"
        "b.n .Lspot_buck_clock_mid_done\n"
        ".Lspot_buck_clock_mid_no:\n"
        "movs r2, #0\n"
        ".Lspot_buck_clock_mid_done:\n"
        "uxtb r2, r2\n"
        "cmp r2, #0\n"
        "bne.n .Lspot_buck_clock_match\n"
        "adds.w r2, r1, r0, lsl #5\n"
        "ldr.w r2, [r2, #0x200]\n"
        "ubfx r2, r2, #8, #9\n"
        "cmp.w r2, #0x100\n"
        "blt.n .Lspot_buck_clock_gpio_no\n"
        "adds.w r1, r1, r0, lsl #5\n"
        "ldr.w r1, [r1, #0x200]\n"
        "ubfx r1, r1, #8, #9\n"
        "cmp.w r1, #0x1e0\n"
        "bge.n .Lspot_buck_clock_gpio_no\n"
        "movs r1, #1\n"
        "b.n .Lspot_buck_clock_gpio_done\n"
        ".Lspot_buck_clock_gpio_no:\n"
        "movs r1, #0\n"
        ".Lspot_buck_clock_gpio_done:\n"
        "eors r1, r1, #1\n"
        "b.n .Lspot_buck_clock_match_fold\n"
        ".Lspot_buck_clock_match:\n"
        "movs r1, #0\n"
        ".Lspot_buck_clock_match_fold:\n"
        "eors r1, r1, #1\n"
        "b.n .Lspot_buck_clock_ready\n"
        ".Lspot_buck_timer_inactive:\n"
        "movs r1, #0\n"
        ".Lspot_buck_clock_ready:\n"
        "uxtb r1, r1\n"
        "cmp r1, #0\n"
        "beq.n .Lspot_buck_timer_next\n"
        "movs r0, #1\n"
        "ldr.w r1, [pc, #0xa2c]\n"
        "strb r0, [r1]\n"
        "b.n .Lspot_buck_return\n"
        ".Lspot_buck_clear:\n"
        "movs r0, #0\n"
        "ldr.w r1, [pc, #0xa20]\n"
        "strb r0, [r1]\n"
        ".Lspot_buck_return:\n"
        "pop {r0, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_buck_state {
    open_cfw_spotmgr_buck_u32 dev_power_status;
    open_cfw_spotmgr_buck_u32 audss_power_status;
    open_cfw_spotmgr_buck_u8 temperature_range;
    open_cfw_spotmgr_buck_u8 syspll_enabled;
    open_cfw_spotmgr_buck_u8 stimer_running;
    open_cfw_spotmgr_buck_u8 stimer_clock;
    open_cfw_spotmgr_buck_u32 timer_ctrl[16];
    open_cfw_spotmgr_buck_u32 timer_global_enable;
    open_cfw_spotmgr_buck_u8 force_buck_active;
} open_cfw_spotmgr_buck_state;

static open_cfw_spotmgr_buck_u32 open_cfw_spotmgr_buck_clock_matches(
    open_cfw_spotmgr_buck_u32 clock)
{
    return (clock < 6U) || ((clock >= 19U) && (clock < 25U)) ||
        ((clock >= 0x100U) && (clock < 0x1e0U));
}

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_buck_deepsleep_state_42a08c(
    open_cfw_spotmgr_buck_state *state)
{
    open_cfw_spotmgr_buck_u32 index;

    if ((state->temperature_range == 3U) ||
        ((state->dev_power_status & 0x3fffffffU) != 0U) ||
        ((state->audss_power_status & 0x4c4U) != 0U) ||
        (state->syspll_enabled != 0U)) {
        state->force_buck_active = 1U;
        return;
    }

    if ((state->stimer_running != 0U) &&
        (state->stimer_clock >= 1U) && (state->stimer_clock < 3U)) {
        state->force_buck_active = 1U;
        return;
    }

    for (index = 0U; index < 16U; ++index) {
        open_cfw_spotmgr_buck_u32 control = state->timer_ctrl[index];
        if (((control & 1U) != 0U) &&
            ((state->timer_global_enable & (1U << index)) != 0U) &&
            open_cfw_spotmgr_buck_clock_matches((control >> 8) & 0x1ffU)) {
            state->force_buck_active = 1U;
            return;
        }
    }
    state->force_buck_active = 0U;
}

#endif
