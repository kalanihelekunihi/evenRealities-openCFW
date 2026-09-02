/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager stepwise temperature-transition dispatcher
 * authenticated at G2 bootloader address 0x0042A43A.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_temperature_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_temperature_u8;

#if defined(__arm__) || defined(__thumb__)

extern open_cfw_spotmgr_temperature_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
    open_cfw_spotmgr_temperature_u32 target_state,
    open_cfw_spotmgr_temperature_u32 current_state,
    open_cfw_spotmgr_temperature_u8 *sequence);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_temperature_u32
open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a(
    open_cfw_spotmgr_temperature_u32 target_state __attribute__((unused)),
    open_cfw_spotmgr_temperature_u32 current_state __attribute__((unused)),
    open_cfw_spotmgr_temperature_u32 target_ton_state __attribute__((unused)),
    open_cfw_spotmgr_temperature_u32 current_ton_state __attribute__((unused)))
{
    __asm volatile(
        "push.w {r2, r3, r4, r5, r6, r7, r8, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "movs r6, r2\n"
        "movs r7, r3\n"
        "movs r0, #0\n"
        "movs r0, #0\n"
        "movs r0, #0x1a\n"
        "strb.w r0, [sp]\n"
        "cmp r5, r4\n"
        "bhs.n .Lspot_temp_descending\n"
        "mov r8, r5\n"
        ".Lspot_temp_up_test:\n"
        "cmp r8, r4\n"
        "bhs.n .Lspot_temp_return\n"
        "adds.w r0, r8, #1\n"
        "mov r2, sp\n"
        "mov r1, r8\n"
        "bl open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4\n"
        "cmp r0, #0\n"
        "bne.n .Lspot_temp_up_next\n"
        "movs r3, r7\n"
        "movs r2, r6\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        "ldr.w ip, [pc, #0x848]\n"
        "ldrb.w lr, [sp]\n"
        "ldr.w ip, [ip, lr, lsl #2]\n"
        "blx ip\n"
        ".Lspot_temp_up_next:\n"
        "adds.w r8, r8, #1\n"
        "b.n .Lspot_temp_up_test\n"
        ".Lspot_temp_descending:\n"
        "mov r8, r5\n"
        "b.n .Lspot_temp_down_test\n"
        ".Lspot_temp_down_body:\n"
        "subs.w r0, r8, #1\n"
        "mov r2, sp\n"
        "mov r1, r8\n"
        "bl open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4\n"
        "cmp r0, #0\n"
        "bne.n .Lspot_temp_down_next\n"
        "movs r3, r7\n"
        "movs r2, r6\n"
        "movs r1, r5\n"
        "movs r0, r4\n"
        "ldr.w ip, [pc, #0x818]\n"
        "ldrb.w lr, [sp]\n"
        "ldr.w ip, [ip, lr, lsl #2]\n"
        "blx ip\n"
        ".Lspot_temp_down_next:\n"
        "subs.w r8, r8, #1\n"
        ".Lspot_temp_down_test:\n"
        "cmp r4, r8\n"
        "blo.n .Lspot_temp_down_body\n"
        ".Lspot_temp_return:\n"
        "pop.w {r0, r1, r4, r5, r6, r7, r8, pc}\n"
    );
}

#else

extern open_cfw_spotmgr_temperature_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
    open_cfw_spotmgr_temperature_u32 target_state,
    open_cfw_spotmgr_temperature_u32 current_state,
    open_cfw_spotmgr_temperature_u8 *sequence);

typedef open_cfw_spotmgr_temperature_u32
(*open_cfw_spotmgr_temperature_observer)(
    open_cfw_spotmgr_temperature_u8 sequence,
    open_cfw_spotmgr_temperature_u32 target_state,
    open_cfw_spotmgr_temperature_u32 current_state,
    open_cfw_spotmgr_temperature_u32 target_ton_state,
    open_cfw_spotmgr_temperature_u32 current_ton_state,
    void *context);

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_temperature_u32
open_cfw_bootloader_spotmgr_temperature_transition_separate_42a43a(
    open_cfw_spotmgr_temperature_u32 target_state,
    open_cfw_spotmgr_temperature_u32 current_state,
    open_cfw_spotmgr_temperature_u32 target_ton_state,
    open_cfw_spotmgr_temperature_u32 current_ton_state,
    open_cfw_spotmgr_temperature_observer observer,
    void *context)
{
    open_cfw_spotmgr_temperature_u32 status = 0U;
    open_cfw_spotmgr_temperature_u32 starting_state;
    open_cfw_spotmgr_temperature_u32 ending_state;
    open_cfw_spotmgr_temperature_u8 sequence = 26U;

    if (target_state > current_state) {
        for (starting_state = current_state; starting_state < target_state;
             ++starting_state) {
            ending_state = starting_state + 1U;
            if (open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
                    ending_state, starting_state, &sequence) == 0U) {
                status = observer(sequence, target_state, current_state,
                                  target_ton_state, current_ton_state, context);
            }
        }
    } else {
        for (starting_state = current_state; starting_state > target_state;
             --starting_state) {
            ending_state = starting_state - 1U;
            if (open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
                    ending_state, starting_state, &sequence) == 0U) {
                status = observer(sequence, target_state, current_state,
                                  target_ton_state, current_ton_state, context);
            }
        }
    }
    return status;
}

#endif
