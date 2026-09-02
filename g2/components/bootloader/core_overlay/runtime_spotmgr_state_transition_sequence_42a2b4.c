/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Apollo510 SPOT-manager power-state transition-sequence selector
 * authenticated at G2 bootloader address 0x0042A2B4.
 */

typedef __UINT32_TYPE__ open_cfw_spotmgr_sequence_u32;
typedef __UINT8_TYPE__ open_cfw_spotmgr_sequence_u8;

#if defined(__arm__) || defined(__thumb__)

extern void open_cfw_bootloader_memcpy_aligned_4156ac(void);

__attribute__((used, noinline, naked, visibility("default")))
open_cfw_spotmgr_sequence_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
    open_cfw_spotmgr_sequence_u32 target_state __attribute__((unused)),
    open_cfw_spotmgr_sequence_u32 current_state __attribute__((unused)),
    open_cfw_spotmgr_sequence_u8 *sequence __attribute__((unused)))
{
    __asm volatile(
        "push {r3, r4, r5, r6, lr}\n"
        "sub sp, #0x1c\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "movs r6, r2\n"
        "mov r0, sp\n"
        "ldr.w r1, [pc, #0x9f0]\n"
        "movs r2, #0x1c\n"
        "bl open_cfw_bootloader_memcpy_aligned_4156ac\n"
        "mov r1, sp\n"
        "movs r2, r5\n"
        "lsrs r2, r2, #2\n"
        "movs r0, #5\n"
        "muls r2, r0, r2\n"
        "add.w r0, r1, r2\n"
        "movs r1, r4\n"
        "lsrs r1, r1, #2\n"
        "ldrb r0, [r0, r1]\n"
        "strb r0, [r6]\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0x1a\n"
        "bne.n .Lspot_sequence_valid\n"
        "movs r0, #7\n"
        "b.n .Lspot_sequence_return\n"
        ".Lspot_sequence_valid:\n"
        "cmp r5, #0\n"
        "bne.n .Lspot_sequence_check_8_to_0\n"
        "cmp r4, #8\n"
        "bne.n .Lspot_sequence_check_8_to_0\n"
        "movs r0, #0x15\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_check_8_12\n"
        ".Lspot_sequence_check_8_to_0:\n"
        "cmp r5, #8\n"
        "bne.n .Lspot_sequence_check_8_12\n"
        "cmp r4, #0\n"
        "bne.n .Lspot_sequence_check_8_12\n"
        "movs r0, #0x16\n"
        "strb r0, [r6]\n"
        ".Lspot_sequence_check_8_12:\n"
        "cmp r5, #8\n"
        "bne.n .Lspot_sequence_check_12_to_8\n"
        "cmp r4, #0xc\n"
        "beq.n .Lspot_sequence_set_23\n"
        ".Lspot_sequence_check_12_to_8:\n"
        "cmp r5, #0xc\n"
        "bne.n .Lspot_sequence_check_temp\n"
        "cmp r4, #8\n"
        "bne.n .Lspot_sequence_check_temp\n"
        ".Lspot_sequence_set_23:\n"
        "movs r0, #0x17\n"
        "strb r0, [r6]\n"
        ".Lspot_sequence_check_temp:\n"
        "ldrb r0, [r6]\n"
        "cmp r0, #0x19\n"
        "bne.w .Lspot_sequence_success\n"

        "tst.w r5, #3\n"
        "beq.n .Lspot_sequence_gt50_to_le50\n"
        "movs r0, r5\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_gt50_to_le50\n"
        "tst.w r4, #3\n"
        "bne.n .Lspot_sequence_gt50_to_le50\n"
        "movs r0, r4\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_gt50_to_le50\n"
        "cmp r5, #9\n"
        "bne.n .Lspot_sequence_le50_second\n"
        "cmp r4, #8\n"
        "bne.n .Lspot_sequence_le50_second\n"
        "movs r0, #0xb\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_le50_second:\n"
        "cmp r5, #1\n"
        "bne.n .Lspot_sequence_set_24_a\n"
        "cmp r4, #0\n"
        "bne.n .Lspot_sequence_set_24_a\n"
        "movs r0, #0xc\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_set_24_a:\n"
        "movs r0, #0x18\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"

        ".Lspot_sequence_gt50_to_le50:\n"
        "tst.w r5, #3\n"
        "bne.n .Lspot_sequence_le0_to_gt0\n"
        "movs r0, r5\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_le0_to_gt0\n"
        "tst.w r4, #3\n"
        "beq.n .Lspot_sequence_le0_to_gt0\n"
        "movs r0, r4\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_le0_to_gt0\n"
        "cmp r5, #8\n"
        "bne.n .Lspot_sequence_gt50_second\n"
        "cmp r4, #9\n"
        "bne.n .Lspot_sequence_gt50_second\n"
        "movs r0, #0xd\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_gt50_second:\n"
        "cmp r5, #0\n"
        "bne.n .Lspot_sequence_set_24_b\n"
        "cmp r4, #1\n"
        "bne.n .Lspot_sequence_set_24_b\n"
        "movs r0, #0xe\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_set_24_b:\n"
        "movs r0, #0x18\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"

        ".Lspot_sequence_le0_to_gt0:\n"
        "ands r0, r5, #3\n"
        "cmp r0, #2\n"
        "blo.n .Lspot_sequence_gt0_to_le0\n"
        "movs r0, r5\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_gt0_to_le0\n"
        "ands r0, r4, #3\n"
        "cmp r0, #2\n"
        "bhs.n .Lspot_sequence_gt0_to_le0\n"
        "movs r0, r4\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_gt0_to_le0\n"
        "cmp r5, #2\n"
        "bne.n .Lspot_sequence_le0_second\n"
        "cmp r4, #1\n"
        "beq.n .Lspot_sequence_set_15\n"
        ".Lspot_sequence_le0_second:\n"
        "cmp r5, #0xa\n"
        "bne.n .Lspot_sequence_set_16\n"
        "cmp r4, #9\n"
        "bne.n .Lspot_sequence_set_16\n"
        ".Lspot_sequence_set_15:\n"
        "movs r0, #0xf\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_set_16:\n"
        "movs r0, #0x10\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"

        ".Lspot_sequence_gt0_to_le0:\n"
        "ands r0, r5, #3\n"
        "cmp r0, #2\n"
        "bhs.n .Lspot_sequence_ten_eleven\n"
        "movs r0, r5\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_ten_eleven\n"
        "ands r0, r4, #3\n"
        "cmp r0, #2\n"
        "blo.n .Lspot_sequence_ten_eleven\n"
        "movs r0, r4\n"
        "lsrs r0, r0, #2\n"
        "cmp r0, #5\n"
        "bhs.n .Lspot_sequence_ten_eleven\n"
        "cmp r5, #9\n"
        "bne.n .Lspot_sequence_gt0_second\n"
        "cmp r4, #0xa\n"
        "bne.n .Lspot_sequence_gt0_second\n"
        "movs r0, #0x11\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_gt0_second:\n"
        "cmp r5, #1\n"
        "bne.n .Lspot_sequence_set_19\n"
        "cmp r4, #2\n"
        "bne.n .Lspot_sequence_set_19\n"
        "movs r0, #0x12\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_set_19:\n"
        "movs r0, #0x13\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"

        ".Lspot_sequence_ten_eleven:\n"
        "cmp r5, #0xa\n"
        "bne.n .Lspot_sequence_check_11_to_10\n"
        "cmp r4, #0xb\n"
        "beq.n .Lspot_sequence_set_20\n"
        ".Lspot_sequence_check_11_to_10:\n"
        "cmp r5, #0xb\n"
        "bne.n .Lspot_sequence_set_24_c\n"
        "cmp r4, #0xa\n"
        "bne.n .Lspot_sequence_set_24_c\n"
        ".Lspot_sequence_set_20:\n"
        "movs r0, #0x14\n"
        "strb r0, [r6]\n"
        "b.n .Lspot_sequence_success\n"
        ".Lspot_sequence_set_24_c:\n"
        "movs r0, #0x18\n"
        "strb r0, [r6]\n"
        ".Lspot_sequence_success:\n"
        "movs r0, #0\n"
        ".Lspot_sequence_return:\n"
        "add sp, #0x20\n"
        "pop {r4, r5, r6, pc}\n"
    );
}

#else

static const open_cfw_spotmgr_sequence_u8
open_cfw_spotmgr_transition_table[5][5] = {
    {25U, 0U, 1U, 26U, 0U},
    {2U, 25U, 26U, 3U, 3U},
    {4U, 26U, 25U, 5U, 26U},
    {26U, 6U, 7U, 25U, 8U},
    {2U, 9U, 26U, 10U, 25U},
};

static open_cfw_spotmgr_sequence_u32
open_cfw_spotmgr_sequence_group(open_cfw_spotmgr_sequence_u32 state)
{
    return state >> 2;
}

static int open_cfw_spotmgr_sequence_gt50(
    open_cfw_spotmgr_sequence_u32 state)
{
    return ((state & 3U) == 0U) &&
           (open_cfw_spotmgr_sequence_group(state) <= 4U);
}

static int open_cfw_spotmgr_sequence_le50(
    open_cfw_spotmgr_sequence_u32 state)
{
    return ((state & 3U) > 0U) &&
           (open_cfw_spotmgr_sequence_group(state) <= 4U);
}

static int open_cfw_spotmgr_sequence_gt0(
    open_cfw_spotmgr_sequence_u32 state)
{
    return ((state & 3U) <= 1U) &&
           (open_cfw_spotmgr_sequence_group(state) <= 4U);
}

static int open_cfw_spotmgr_sequence_le0(
    open_cfw_spotmgr_sequence_u32 state)
{
    return ((state & 3U) >= 2U) &&
           (open_cfw_spotmgr_sequence_group(state) <= 4U);
}

__attribute__((used, noinline, visibility("default")))
open_cfw_spotmgr_sequence_u32
open_cfw_bootloader_spotmgr_state_transition_sequence_42a2b4(
    open_cfw_spotmgr_sequence_u32 target_state,
    open_cfw_spotmgr_sequence_u32 current_state,
    open_cfw_spotmgr_sequence_u8 *sequence)
{
    *sequence = open_cfw_spotmgr_transition_table
        [open_cfw_spotmgr_sequence_group(current_state)]
        [open_cfw_spotmgr_sequence_group(target_state)];
    if (*sequence == 26U) {
        return 7U;
    }
    if ((current_state == 0U) && (target_state == 8U)) {
        *sequence = 21U;
    } else if ((current_state == 8U) && (target_state == 0U)) {
        *sequence = 22U;
    }
    if (((current_state == 8U) && (target_state == 12U)) ||
        ((current_state == 12U) && (target_state == 8U))) {
        *sequence = 23U;
    }
    if (*sequence == 25U) {
        if (open_cfw_spotmgr_sequence_le50(current_state) &&
            open_cfw_spotmgr_sequence_gt50(target_state)) {
            if ((current_state == 9U) && (target_state == 8U)) {
                *sequence = 11U;
            } else if ((current_state == 1U) && (target_state == 0U)) {
                *sequence = 12U;
            } else {
                *sequence = 24U;
            }
        } else if (open_cfw_spotmgr_sequence_gt50(current_state) &&
                   open_cfw_spotmgr_sequence_le50(target_state)) {
            if ((current_state == 8U) && (target_state == 9U)) {
                *sequence = 13U;
            } else if ((current_state == 0U) && (target_state == 1U)) {
                *sequence = 14U;
            } else {
                *sequence = 24U;
            }
        } else if (open_cfw_spotmgr_sequence_le0(current_state) &&
                   open_cfw_spotmgr_sequence_gt0(target_state)) {
            if (((current_state == 2U) && (target_state == 1U)) ||
                ((current_state == 10U) && (target_state == 9U))) {
                *sequence = 15U;
            } else {
                *sequence = 16U;
            }
        } else if (open_cfw_spotmgr_sequence_gt0(current_state) &&
                   open_cfw_spotmgr_sequence_le0(target_state)) {
            if ((current_state == 9U) && (target_state == 10U)) {
                *sequence = 17U;
            } else if ((current_state == 1U) && (target_state == 2U)) {
                *sequence = 18U;
            } else {
                *sequence = 19U;
            }
        } else if (((current_state == 10U) && (target_state == 11U)) ||
                   ((current_state == 11U) && (target_state == 10U))) {
            *sequence = 20U;
        } else {
            *sequence = 24U;
        }
    }
    return 0U;
}

#endif
