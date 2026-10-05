/* SPDX-License-Identifier: BSD-3-Clause */
// Copyright (c) 2025, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//

#ifndef OPENCFW_AMBIQ_MSPI_COMPAT_H
#define OPENCFW_AMBIQ_MSPI_COMPAT_H
#include "ambiq_mspi_interrupts.h"
#include <stddef.h>

/* Prefix definition copied from pinned am_hal_global.h; no full HAL state. */
typedef union {
    uint32_t u32;
    struct { uint32_t magic:24, bInit:1, bEnable:1, resv:6; } s;
} am_hal_handle_prefix_t;
/* Sparse STOCK view: unproven fields remain opaque. The public SDK's complete
 * state layout differs and must not be instantiated as a stock replacement.
 * pTCB is a 32-bit target address slot, tested only for nonzero by this subset. */
typedef struct {
    am_hal_handle_prefix_t prefix; uint32_t ui32Module;
    uint8_t opaque08[0x18-0x08];
    uint32_t pTCB; uint32_t opaque1c; uint32_t ui32NumCQEntries;
    uint8_t opaque24[0x840-0x24];
    uint32_t ui32NumHPEntries;
    uint8_t opaque844[0x8cc-0x844];
    uint32_t ui32XIPOffMinDelay;
} am_hal_mspi_state_t;
/* Only the interrupt-register window is represented. */
typedef struct {
    uint32_t reserved00[0x90/4];
    union {
        volatile uint32_t DEV0XIP;
        struct { volatile uint32_t XIPEN0:1, reserved:31; } DEV0XIP_b;
    };
    uint32_t reserved94[(0x200-0x94)/4];
    volatile uint32_t INTEN, INTSTAT, INTCLR;
} opencfw_mspi_registers_t;
_Static_assert(sizeof(am_hal_handle_prefix_t)==4,"HAL prefix ABI");
_Static_assert(offsetof(am_hal_mspi_state_t,ui32Module)==4,"HAL module ABI");
_Static_assert(offsetof(am_hal_mspi_state_t,pTCB)==0x18,"stock TCB slot ABI");
_Static_assert(offsetof(am_hal_mspi_state_t,ui32NumCQEntries)==0x20,"stock CQ count ABI");
_Static_assert(offsetof(am_hal_mspi_state_t,ui32NumHPEntries)==0x840,"stock HP count ABI");
_Static_assert(offsetof(am_hal_mspi_state_t,ui32XIPOffMinDelay)==0x8cc,"stock XIP delay ABI");
_Static_assert(sizeof(am_hal_mspi_state_t)==0x8d0,"sparse view extent");
_Static_assert(offsetof(opencfw_mspi_registers_t,DEV0XIP)==0x90,"XIP register ABI");
_Static_assert(offsetof(opencfw_mspi_registers_t,INTEN)==0x200,"INTEN ABI");
_Static_assert(offsetof(opencfw_mspi_registers_t,INTSTAT)==0x204,"INTSTAT ABI");
_Static_assert(offsetof(opencfw_mspi_registers_t,INTCLR)==0x208,"INTCLR ABI");
#define AM_HAL_MAGIC_MSPI 0xBEBEBE
#define AM_HAL_MSPI_CHK_HANDLE(h) ((h) && ((am_hal_handle_prefix_t *)(h))->s.bInit && (((am_hal_handle_prefix_t *)(h))->s.magic == AM_HAL_MAGIC_MSPI))
#define AM_HAL_STATUS_SUCCESS 0u
#define AM_HAL_STATUS_INVALID_HANDLE 2u
#define AM_HAL_STATUS_IN_USE 3u
/* External provider contracts; no real CQ/clock implementation supplied here. */
uint32_t mspi_cq_disable(void *handle);
uint32_t mspi_cq_term(void *handle);
void am_hal_delay_us(uint32_t duration);
/* Host tests replace only address mapping, preserving the selected bodies. */
#ifdef OPENCFW_MSPI_HOST_FIXTURE
opencfw_mspi_registers_t *opencfw_mspi_fixture_registers(uint32_t module);
#define MSPIn(module) opencfw_mspi_fixture_registers(module)
#else
#define MSPIn(module) ((opencfw_mspi_registers_t *)(uintptr_t)(0x40060000u + (uint32_t)(module)*0x1000u))
#endif
#endif
