/*
 * SPDX-License-Identifier: BSD-3-Clause
 * Port of Apollo510 SPOT PCM2.2 transitions 0 and 2 guided by AmbiqSuite
 * release_5p1p0beta-2927d425bf, upstream pin 5efc0228528a8adce5eae0d226fac85d2551eb3b.
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 * NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
#include <stdbool.h>
#include <stdint.h>

#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define R8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define W8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major);
extern void opencfw_hal_delay_us(uint32_t microseconds);
extern uint32_t opencfw_boot_icache_enable(void);
extern uint32_t opencfw_pcm22_icache_disable(void);
extern uint32_t opencfw_pcm22_timer_service(void);
extern void opencfw_pcm22_spot_timer_start(uint32_t wait);
extern void opencfw_pcm22_spot_timer_stop(void);

typedef struct {
    uint32_t target_state, current_state, target_ton, current_ton;
    uint32_t target_word, current_word, vddclv_word;
    uint32_t new_vddf, current_vddf, new_vddc, current_vddc;
    uint32_t new_core_active, new_core_tempco;
    uint32_t vddclv[4];
} event_a_sequence_context;

static event_a_sequence_context sequence_context(uint32_t target_state,
                                                  uint32_t current_state,
                                                  uint32_t target_ton,
                                                  uint32_t current_ton)
{
    const volatile uint32_t *const profile =
        (const volatile uint32_t *)(uintptr_t)0x20026ba0U;
    event_a_sequence_context c = {0};
    c.target_state = target_state;
    c.current_state = current_state;
    c.target_ton = target_ton;
    c.current_ton = current_ton;
    c.target_word = profile[1U + target_state];
    c.current_word = profile[1U + current_state];
    c.vddclv_word = profile[0x64U / 4U];
    c.new_vddf = c.target_word & 0x7fU;
    c.current_vddf = c.current_word & 0x7fU;
    c.new_core_active = (c.target_word >> 7) & 0x3ffU;
    c.new_core_tempco = (c.target_word >> 17) & 0x0fU;
    c.new_vddc = (c.target_word >> 21) & 0x7fU;
    c.current_vddc = (c.current_word >> 21) & 0x7fU;
    c.vddclv[0] = c.vddclv_word & 0x7fU;
    c.vddclv[1] = (c.vddclv_word >> 7) & 0x7fU;
    c.vddclv[2] = (c.vddclv_word >> 14) & 0x7fU;
    c.vddclv[3] = (c.vddclv_word >> 21) & 0x7fU;
    return c;
}

static uint32_t packed_vddclv(const event_a_sequence_context *c)
{
    return c->vddclv[0] | (c->vddclv[1] << 8) |
           (c->vddclv[2] << 16) | (c->vddclv[3] << 24);
}

static void store_sequence_targets(const event_a_sequence_context *c)
{
    W32(0x200270c0U) = c->target_ton;
    W32(0x200270c4U) = c->target_state;
    W32(0x200270b8U) = c->new_core_active;
    W32(0x200270bcU) = c->new_core_tempco;
    W32(0x200270b0U) = c->new_vddc;
    W32(0x200270b4U) = c->new_vddf;
}

static void set_low7(uint32_t address, uint32_t value)
{
    W32(address) = (R32(address) & ~0x7fU) | (value & 0x7fU);
}

static void wait_for_timer_then_service(void)
{
    /* Stock tests TIMERCONTROL enable with LSL #31, i.e. source bit 0. */
    if ((R32(0x400083e0U) & 1U) == 0U) return;
    for (uint32_t i = 0; i < 60U; ++i) {
        if ((R32(0x40008064U) & 0x40000000U) != 0U) break;
        opencfw_hal_delay_us(1U);
    }
    (void)opencfw_pcm22_timer_service();
}

__attribute__((noinline, used))
uint32_t event_a_pcm22_transition_sequence_0(uint32_t target_state,
                                              uint32_t current_state,
                                              uint32_t target_ton,
                                              uint32_t current_ton)
{
    event_a_sequence_context c = sequence_context(target_state,current_state,
                                                   target_ton,current_ton);
    uint32_t enable_icache = 0U;

    if ((R32(0x400083e0U) & 1U) != 0U) {
        if (target_state == R32(0x20000154U)) {
            event_a_power_ton_adjust(target_ton,target_state);
            set_low7(0x40020044U,c.new_vddc);
            opencfw_pcm22_spot_timer_stop();
            W8(0x2000055aU) = 0x1aU;
            return packed_vddclv(&c);
        }
        wait_for_timer_then_service();
    }

    store_sequence_targets(&c);
    event_a_power_ton_adjust(target_ton,target_state);
    uint32_t diff = c.new_vddf > c.current_vddf ?
                    2U * (c.new_vddf - c.current_vddf) : 0U;
    uint32_t boosted = c.current_vddf + diff;
    if (boosted > 0x7fU) boosted = 0x7fU;
    set_low7(0x4002004cU,boosted);
    opencfw_hal_delay_us(50U);
    set_low7(0x4002004cU,c.new_vddf);

    if ((R32(0xe000ed14U) & 0x20000U) != 0U) {
        uint32_t status = opencfw_pcm22_icache_disable();
        if (status != 0U) return status;
        enable_icache = 1U;
    }
    W32(0x4002037cU) |= 0x00010000U;
    W32(0x4002037cU) |= 0x02000000U;
    opencfw_hal_delay_us(20U);
    if (enable_icache != 0U) {
        uint32_t status = opencfw_boot_icache_enable();
        if (status != 0U) return status;
    }
    /* PCM2.2 applies the timer-control trims as two distinct RMW writes.
     * Keep both writes and the hardware field positions from the public
     * implementation: tempco[3:0] at [13:10], active[9:0] at [9:0]. */
    W32(0x40020080U) = (R32(0x40020080U) & ~0x00003c00U) |
                       (c.new_core_tempco << 10);
    W32(0x40020080U) = (R32(0x40020080U) & ~0x000003ffU) |
                       c.new_core_active;
    set_low7(0x40020044U,c.new_vddc);
    return packed_vddclv(&c);
}

__attribute__((noinline, used))
uint32_t event_a_pcm22_transition_sequence_2(uint32_t target_state,
                                              uint32_t current_state,
                                              uint32_t target_ton,
                                              uint32_t current_ton)
{
    event_a_sequence_context c = sequence_context(target_state,current_state,
                                                   target_ton,current_ton);
    wait_for_timer_then_service();
    store_sequence_targets(&c);
    event_a_power_ton_adjust(target_ton,target_state);

    /* TVRGFACTTRIM2 + (TVRGFACTTRIM2 - TVRGFACTTRIM1), saturate to 7 bits. */
    const volatile uint32_t *const profile =
        (const volatile uint32_t *)(uintptr_t)0x20026ba0U;
    /* Stock uses the fixed profile trim at base + 0x50, independent of the
     * requested state, before applying the VDDc ramp. */
    uint32_t vddf2 = profile[0x50U / 4U] & 0x7fU;
    set_low7(0x4002004cU,vddf2);

    uint32_t diff = c.new_vddc > c.current_vddc ?
                    2U * (c.new_vddc - c.current_vddc) : 0U;
    uint32_t boosted = c.current_vddc + diff;
    if (boosted > 0x7fU) boosted = 0x7fU;
    set_low7(0x40020044U,boosted);
    W32(0x20000154U) = target_state;
    opencfw_pcm22_spot_timer_start(50U);
    W8(0x2000055aU) = 2U;
    return packed_vddclv(&c);
}
