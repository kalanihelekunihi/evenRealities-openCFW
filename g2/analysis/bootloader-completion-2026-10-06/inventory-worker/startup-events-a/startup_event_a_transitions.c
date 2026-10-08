/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Apollo510 SPOT transition selector and ordered temperature dispatcher.
 *
 * Behavior follows AmbiqSuite 5.1.0 PCM2.2 spotmgr_state_transition_sequence_determine
 * and spotmgr_temperature_transition_separate. The 5x5 selector bytes are
 * authenticated from the locked image at 0x433498 (SHA-256
 * d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8).
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 1. Source redistributions retain this notice, conditions, and disclaimer.
 * 2. Binary redistributions reproduce them in documentation/materials.
 * 3. Neither Ambiq Micro's name nor contributors' names may endorse products
 *    without prior written permission.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES.
 */
#include <stdint.h>

enum {
    EVENT_A_TRANSITION_TEMP = 25,
    EVENT_A_TRANSITION_INVALID = 26,
    EVENT_A_TRANSITION_INVALID_STATUS = 7,
};

/* The locked image literal at 0x42acb4 points to this 28-byte table. */
static const uint8_t event_a_transition_table[5][5] = {
    {25, 0, 1, 26, 0},
    {2, 25, 26, 3, 3},
    {4, 26, 25, 5, 26},
    {26, 6, 7, 25, 8},
    {2, 9, 26, 10, 25},
};

static int event_a_gt50(uint32_t state)
{
    return ((state & 3U) == 0U) && ((state >> 2) <= 4U);
}

static int event_a_le50(uint32_t state)
{
    return ((state & 3U) != 0U) && ((state >> 2) <= 4U);
}

static int event_a_gt0(uint32_t state)
{
    return ((state & 3U) <= 1U) && ((state >> 2) <= 4U);
}

static int event_a_le0(uint32_t state)
{
    return ((state & 3U) >= 2U) && ((state >> 2) <= 4U);
}

/* Inputs are documented SPOT state indices 0..19, as in the firmware caller. */
__attribute__((noinline, used))
uint32_t event_a_state_transition_sequence(uint32_t target_state,
                                          uint32_t current_state,
                                          uint8_t *sequence)
{
    *sequence = event_a_transition_table[current_state >> 2][target_state >> 2];
    if (*sequence == EVENT_A_TRANSITION_INVALID) {
        return EVENT_A_TRANSITION_INVALID_STATUS;
    }

    if (current_state == 0U && target_state == 8U) {
        *sequence = 21U;
    } else if (current_state == 8U && target_state == 0U) {
        *sequence = 22U;
    }
    if ((current_state == 8U && target_state == 12U) ||
        (current_state == 12U && target_state == 8U)) {
        *sequence = 23U;
    }

    if (*sequence == EVENT_A_TRANSITION_TEMP) {
        if (event_a_le50(current_state) && event_a_gt50(target_state)) {
            if (current_state == 9U && target_state == 8U) {
                *sequence = 11U;
            } else if (current_state == 1U && target_state == 0U) {
                *sequence = 12U;
            } else {
                *sequence = 24U;
            }
        } else if (event_a_gt50(current_state) && event_a_le50(target_state)) {
            if (current_state == 8U && target_state == 9U) {
                *sequence = 13U;
            } else if (current_state == 0U && target_state == 1U) {
                *sequence = 14U;
            } else {
                *sequence = 24U;
            }
        } else if (event_a_le0(current_state) && event_a_gt0(target_state)) {
            if ((current_state == 2U && target_state == 1U) ||
                (current_state == 10U && target_state == 9U)) {
                *sequence = 15U;
            } else {
                *sequence = 16U;
            }
        } else if (event_a_gt0(current_state) && event_a_le0(target_state)) {
            if (current_state == 9U && target_state == 10U) {
                *sequence = 17U;
            } else if (current_state == 1U && target_state == 2U) {
                *sequence = 18U;
            } else {
                *sequence = 19U;
            }
        } else if ((current_state == 10U && target_state == 11U) ||
                   (current_state == 11U && target_state == 10U)) {
            *sequence = 20U;
        } else {
            *sequence = 24U;
        }
    }
    return 0U;
}

typedef uint32_t (*event_a_sequence_callback)(uint32_t, uint32_t,
                                              uint32_t, uint32_t);

/* Installed callback table is supplied by SPOT runtime at this fixed ABI. */
#define EVENT_A_CALLBACK_TABLE ((volatile event_a_sequence_callback *)(uintptr_t)0x20000158U)

__attribute__((noinline, used))
void event_a_temperature_transition_separate(uint32_t target_state,
                                             uint32_t current_state,
                                             uint32_t target_ton_state,
                                             uint32_t current_ton_state)
{
    uint8_t sequence = EVENT_A_TRANSITION_INVALID;
    uint32_t starting_state;
    uint32_t ending_state;

    if (target_state > current_state) {
        for (starting_state = current_state; starting_state < target_state;
             ++starting_state) {
            ending_state = starting_state + 1U;
            if (event_a_state_transition_sequence(ending_state, starting_state,
                                                   &sequence) == 0U) {
                (void)EVENT_A_CALLBACK_TABLE[sequence](
                    target_state, current_state,
                    target_ton_state, current_ton_state);
            }
        }
    } else {
        for (starting_state = current_state; starting_state > target_state;
             --starting_state) {
            ending_state = starting_state - 1U;
            if (event_a_state_transition_sequence(ending_state, starting_state,
                                                   &sequence) == 0U) {
                (void)EVENT_A_CALLBACK_TABLE[sequence](
                    target_state, current_state,
                    target_ton_state, current_ton_state);
            }
        }
    }
}

/* PCM2.2's selector 24 is the documented no-op callback. The locked target
 * table points this slot at 0x42a030, whose exact bytes are BX LR. */
__attribute__((noinline, used))
uint32_t event_a_transition_sequence_24(uint32_t target_state,
                                        uint32_t current_state,
                                        uint32_t target_ton_state,
                                        uint32_t current_ton_state)
{
    (void)current_state;
    (void)target_ton_state;
    (void)current_ton_state;
    /* 0x42a030 is `bx lr`; AAPCS returns the incoming first argument in R0. */
    return target_state;
}
