/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Fixed-ABI reconstruction of stock SPOT selector 3 at 0x4283e2.
 *
 * Behavior is reconstructed from the authenticated locked instructions and
 * cross-checked against the pinned Apollo510 PCM2.2 `transition_sequence_3`
 * implementation. Only the transition body is represented here; it uses
 * existing native timer, delay, and TON-adjust providers.
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

#define R32(address) (*(volatile uint32_t *)(uintptr_t)(address))
#define W32(address) (*(volatile uint32_t *)(uintptr_t)(address))

extern void event_a_power_ton_adjust(uint32_t target_ton,
                                     uint32_t target_power);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void opencfw_hal_delay_us(uint32_t delay_us);

static void selector3_wait_for_timer(void)
{
    if ((R32(0x400083e0u) & 1u) != 0u) {
        for (uint32_t elapsed = 0u; elapsed < 60u; ++elapsed) {
            if ((R32(0x40008064u) & 0x40000000u) != 0u) {
                break;
            }
            opencfw_hal_delay_us(1u);
        }
        (void)opencfw_pcm22_timer_service();
    }
}

/* The locked 292-byte routine returns packed VDDCLV bytes in R0 and preserves
 * the incoming current-TON argument in R1 (a 64-bit AAPCS result). */
__attribute__((noinline, used))
uint64_t opencfw_spot_pcm22_transition3(uint32_t target_power,
                                        uint32_t current_power,
                                        uint32_t target_ton,
                                        uint32_t current_ton)
{
    const uintptr_t info = 0x20026ba0u;
    const uint32_t target_word = R32(info + 4u + target_power * 4u);
    const uint32_t current_word = R32(info + 4u + current_power * 4u);
    const uint32_t vddclv = R32(info + 0x64u);
    const uint32_t target_vddf = target_word & 0x7fu;
    const uint32_t current_vddf = current_word & 0x7fu;
    const uint32_t low_target = (vddclv >> ((target_power & 3u) * 7u)) & 0x7fu;
    const uint32_t packed_vddclv = (vddclv & 0x7fu) |
        (((vddclv >> 7) & 0x7fu) << 8) |
        (((vddclv >> 14) & 0x7fu) << 16) |
        (((vddclv >> 21) & 0x7fu) << 24);

    selector3_wait_for_timer();

    W32(0x200270c0u) = target_ton;
    W32(0x200270c4u) = target_power;
    W32(0x200270b8u) = (target_word >> 7) & 0x3ffu;
    W32(0x200270bcu) = (target_word >> 17) & 0x0fu;
    W32(0x200270b0u) = (target_word >> 21) & 0x7fu;
    W32(0x200270b4u) = target_vddf;

    event_a_power_ton_adjust(target_ton, target_power);

    /* Stock computes a signed increase delta and applies a capped VDDF
     * separation boost to the low seven bits of PWRSW0 at 0x40020048. */
    const int32_t delta = (int32_t)(target_vddf - current_vddf);
    const uint32_t doubled_delta = delta > 0 ? (uint32_t)delta * 2u : 0u;
    const uint32_t boost = (current_vddf + doubled_delta < 0x80u)
        ? current_vddf + doubled_delta : 0x7fu;
    uint32_t power_switch = R32(0x4002004cu);
    W32(0x4002004cu) = (power_switch & 0xffffff80u) | boost;

    opencfw_hal_delay_us(50u);

    power_switch = R32(0x4002004cu);
    W32(0x4002004cu) = (power_switch & 0xffffff80u) | target_vddf;

    (void)low_target;
    return ((uint64_t)current_ton << 32) | packed_vddclv;
}
