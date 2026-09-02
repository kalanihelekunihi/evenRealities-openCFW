/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable realization of the Apollo510 SPOT-manager boost-timer interrupt
 * service authenticated at G2 bootloader address 0x0042A04A. The portable
 * form exposes the sequence dispatch and critical-section ordering.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_irq_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_irq_u8;

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_spotmgr_irq_u32
open_cfw_bootloader_critical_save_41b8ec(void);
extern void open_cfw_bootloader_spotmgr_transition_sequence_2b_428378(void);
extern void open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94(void);
extern void open_cfw_bootloader_spotmgr_timer_finish_41ccd6(void);

__attribute__((used, noinline, naked, visibility("default")))
void open_cfw_bootloader_spotmgr_timer_irq_service_42a04a(void)
{
    __asm volatile(
        "push {r7, lr}\n"
        "bl open_cfw_bootloader_critical_save_41b8ec\n"
        "str r0, [sp]\n"
        "ldr.w r0, [pc, #0xb60]\n"
        "ldrb r1, [r0]\n"
        "cmp r1, #2\n"
        "bne.n .Lspotmgr_irq_check_7\n"
        "bl open_cfw_bootloader_spotmgr_transition_sequence_2b_428378\n"
        "b.n .Lspotmgr_irq_finish\n"
        ".Lspotmgr_irq_check_7:\n"
        "ldrb r0, [r0]\n"
        "cmp r0, #7\n"
        "bne.n .Lspotmgr_irq_finish\n"
        "bl open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94\n"
        ".Lspotmgr_irq_finish:\n"
        "bl open_cfw_bootloader_spotmgr_timer_finish_41ccd6\n"
        "ldr r0, [sp]\n"
        "msr primask, r0\n"
        "pop {r0, pc}\n"
    );
}

#else

typedef struct open_cfw_spotmgr_irq_state {
    open_cfw_spotmgr_irq_u8 ongoing_sequence;
    open_cfw_spotmgr_irq_u32 saved_primask;
    open_cfw_spotmgr_irq_u32 current_primask;
    open_cfw_spotmgr_irq_u32 critical_save_calls;
    open_cfw_spotmgr_irq_u32 transition_2b_calls;
    open_cfw_spotmgr_irq_u32 transition_7b_calls;
    open_cfw_spotmgr_irq_u32 timer_finish_calls;
} open_cfw_spotmgr_irq_state;

__attribute__((used, noinline, visibility("default")))
void open_cfw_bootloader_spotmgr_timer_irq_service_42a04a(
    open_cfw_spotmgr_irq_state *state)
{
    open_cfw_spotmgr_irq_u32 token = state->current_primask;
    state->critical_save_calls += 1U;
    state->current_primask = 1U;
    state->saved_primask = token;
    if (state->ongoing_sequence == 2U) {
        state->transition_2b_calls += 1U;
    } else if (state->ongoing_sequence == 7U) {
        state->transition_7b_calls += 1U;
    }
    state->timer_finish_calls += 1U;
    state->current_primask = token;
}

#endif
