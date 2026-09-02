/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager power/Ton trim transition router authenticated at
 * G2 bootloader address 0x0042A4BC.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_trims_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_trims_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc(void);
extern open_cfw_spotmgr_trims_u32
open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a(void);
extern open_cfw_spotmgr_trims_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(void);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_trims_u32
open_cfw_bootloader_spotmgr_power_trims_update_42a4bc(
    open_cfw_spotmgr_trims_u32 target_state __attribute__((unused)),
    open_cfw_spotmgr_trims_u32 current_state __attribute__((unused)),
    open_cfw_spotmgr_trims_u32 target_ton_state __attribute__((unused)),
    open_cfw_spotmgr_trims_u32 current_ton_state __attribute__((unused)))
{
    __asm volatile(
        "push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "movs r6, r2\n"
        "movs r7, r3\n"
        "movs r0, #0x1a\n"
        "strb.w r0, [sp]\n"
        "cmp r4, r5\n"
        "bne.n .Lspot_trims_power_changed\n"
        "cmp r6, r7\n"
        "beq.n .Lspot_trims_return\n"
        "movs r1, r4\n"
        "movs r0, r6\n"
        "bl open_cfw_bootloader_spotmgr_power_ton_adjust_42a1bc\n"
        "b.n .Lspot_trims_return\n"
        ".Lspot_trims_power_changed:\n"
        "movs r0, r4\n"
        "lsrs r0, r0, #2\n"
        "cmp.w r0, r5, lsr #2\n"
        "bne.n .Lspot_trims_different_group\n"
        "movs r3, r7\n"
        "movs r2, r6\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a\n"
        "b.n .Lspot_trims_return\n"
        ".Lspot_trims_different_group:\n"
        "ands r0, r4, #3\n"
        "ands r1, r5, #3\n"
        "cmp r0, r1\n"
        "beq.n .Lspot_trims_group_transition\n"
        "lsrs r0, r5, #2\n"
        "lsls r0, r0, #2\n"
        "ands r8, r4, #3\n"
        "orrs.w r8, r8, r0\n"
        "movs r3, r7\n"
        "movs r2, r6\n"
        "movs r1, r5\n"
        "mov r0, r8\n"
        "bl open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a\n"
        "mov r5, r8\n"
        ".Lspot_trims_group_transition:\n"
        "mov r2, sp\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        "bl open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4\n"
        "cmp r0, #0\n"
        "bne.n .Lspot_trims_return\n"
        "movs r3, r7\n"
        "movs r2, r6\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        "ldr.w r4, [pc, #0x784]\n"
        "ldrb.w r5, [sp]\n"
        "ldr.w r4, [r4, r5, lsl #2]\n"
        "blx r4\n"
        ".Lspot_trims_return:\n"
        "pop.w {r0, r1, r4, r5, r6, r7, r8, pc}\n"
    );
}

#else

extern open_cfw_spotmgr_trims_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
    open_cfw_spotmgr_trims_u32 target_state,
    open_cfw_spotmgr_trims_u32 current_state,
    open_cfw_spotmgr_trims_u8 *sequence);

typedef void (*open_cfw_spotmgr_trims_ton_hook)(
    open_cfw_spotmgr_trims_u32 ton_state,
    open_cfw_spotmgr_trims_u32 power_state,
    void *context);
typedef open_cfw_spotmgr_trims_u32
(*open_cfw_spotmgr_trims_temperature_hook)(
    open_cfw_spotmgr_trims_u32 target_state,
    open_cfw_spotmgr_trims_u32 current_state,
    open_cfw_spotmgr_trims_u32 target_ton_state,
    open_cfw_spotmgr_trims_u32 current_ton_state,
    void *context);
typedef open_cfw_spotmgr_trims_u32
(*open_cfw_spotmgr_trims_sequence_hook)(
    open_cfw_spotmgr_trims_u8 sequence,
    open_cfw_spotmgr_trims_u32 target_state,
    open_cfw_spotmgr_trims_u32 current_state,
    open_cfw_spotmgr_trims_u32 target_ton_state,
    open_cfw_spotmgr_trims_u32 current_ton_state,
    void *context);

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_trims_u32
open_cfw_bootloader_spotmgr_power_trims_update_42a4bc(
    open_cfw_spotmgr_trims_u32 target_state,
    open_cfw_spotmgr_trims_u32 current_state,
    open_cfw_spotmgr_trims_u32 target_ton_state,
    open_cfw_spotmgr_trims_u32 current_ton_state,
    open_cfw_spotmgr_trims_ton_hook ton_hook,
    open_cfw_spotmgr_trims_temperature_hook temperature_hook,
    open_cfw_spotmgr_trims_sequence_hook sequence_hook,
    void *context)
{
    open_cfw_spotmgr_trims_u32 status = 0U;
    open_cfw_spotmgr_trims_u8 sequence = 26U;

    if (target_state == current_state) {
        if (target_ton_state != current_ton_state) {
            ton_hook(target_ton_state, target_state, context);
        }
    } else if ((target_state >> 2) == (current_state >> 2)) {
        status = temperature_hook(target_state, current_state,
                                  target_ton_state, current_ton_state, context);
    } else {
        if ((target_state & 3U) != (current_state & 3U)) {
            open_cfw_spotmgr_trims_u32 middle_state =
                (current_state & ~3U) | (target_state & 3U);
            status = temperature_hook(middle_state, current_state,
                                      target_ton_state, current_ton_state,
                                      context);
            current_state = middle_state;
        }
        if (open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
                target_state, current_state, &sequence) == 0U) {
            status = sequence_hook(sequence, target_state, current_state,
                                   target_ton_state, current_ton_state, context);
        }
    }
    return status;
}

#endif
