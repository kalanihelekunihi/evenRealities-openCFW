//*****************************************************************************
//
//! @file am_hal_cmdq.c
//!
//! @brief Functions for support command queue operations.
//!
//! @addtogroup cmdq_ap510 CMDQ - Command Queue Functionality
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides support functions for command queue (CMDQ)
//!          operations on Apollo5 devices. It supports command queue
//!          initialization, block allocation, status monitoring, and error
//!          handling for efficient hardware command sequencing.
//!
//! @section hal_cmdq_features Key Features
//!
//! 1. @b Command @b Queue: Hardware command queue management and sequencing.
//! 2. @b Block @b Allocation: Dynamic block allocation and release.
//! 3. @b Status @b Monitoring: Real-time command queue status tracking.
//! 4. @b Error @b Handling: Robust error detection and recovery.
//! 5. @b Multi-Module: Support for multiple hardware modules (IOM, MSPI, BLEIF).
//!
//! @section hal_cmdq_functionality Functionality
//!
//! - Initialize and configure command queue
//! - Allocate and release command queue blocks
//! - Monitor command queue status and indices
//! - Handle command queue errors and recovery
//! - Support multi-module command queue operations
//!
//! @section hal_cmdq_usage Usage
//!
//! 1. Initialize CMDQ using am_hal_cmdq_init()
//! 2. Allocate blocks with am_hal_cmdq_alloc_block()
//! 3. Post and release blocks as needed
//! 4. Monitor status and handle errors
//! 5. Terminate or reset command queue as required
//!
//! @section hal_cmdq_configuration Configuration
//!
//! - @b Block @b Size: Configure command queue block sizes
//! - @b Module @b Selection: Set up for IOM, MSPI, or BLEIF modules
//! - @b Error @b Handling: Configure error detection and recovery
//! - @b Status @b Monitoring: Set up status tracking parameters
//*****************************************************************************

//*****************************************************************************
//
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
// This is part of revision release_sdk5p1p0-366b80e084 of the AmbiqSuite Development Package.
//
//*****************************************************************************

#include "ambiq_cmdq.h"
#define AM_HAL_CMDQ_CHK_HANDLE(h) ((h) && ((((am_hal_handle_prefix_t *)(h))->u32 & 0x1ffffffu)==0x1cdcdcdu))
#define AM_HAL_CMDQ_DISABLE_CQ(reg) (*(reg) &= ~1u)
#define AM_REGVAL(reg) (*(reg))
/* Reconstructed stock update_indices 0x538d18. Critical-enter remains an
 * external provider; restore is the observed ARM PRIMASK instruction. */
static void update_indices(am_hal_cmdq_t *q) {
 uint32_t saved=opencfw_cmdq_critical_enter();
 q->curIdx=(q->endIdx & ~255u) | (*q->pReg->regCurIdx & 255u);
 if ((int32_t)(q->endIdx-q->curIdx)<0) q->curIdx-=256u;
 q->cmdQHead=*q->pReg->regCQAddr;
 __asm__ volatile("msr primask, %0" :: "r"(saved) : "memory");
}
uint32_t
am_hal_cmdq_disable(void *pHandle)
{
    am_hal_cmdq_t *pCmdQ = (am_hal_cmdq_t *)pHandle;
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_CMDQ_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if (!pCmdQ->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_SUCCESS;
    }
    AM_HAL_CMDQ_DISABLE_CQ(pCmdQ->pReg->regCQCfg);
    pCmdQ->prefix.s.bEnable = false;
    return AM_HAL_STATUS_SUCCESS;
}
uint32_t
am_hal_cmdq_term(void *pHandle, bool bForce)
{
    am_hal_cmdq_t *pCmdQ = (am_hal_cmdq_t *)pHandle;
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_CMDQ_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION
    update_indices(pCmdQ);
    if (!bForce && (pCmdQ->curIdx != pCmdQ->endIdx))
    {
        return AM_HAL_STATUS_IN_USE;
    }
    pCmdQ->prefix.s.bInit = false;
    // Disable Command Queue
    AM_HAL_CMDQ_DISABLE_CQ(pCmdQ->pReg->regCQCfg);
    AM_REGVAL(pCmdQ->pReg->regCQPause) &= ~pCmdQ->pReg->bitMaskCQPauseIdx;
    return AM_HAL_STATUS_SUCCESS;
}
/* Stock sparse state uses a 32-bit queue handle at +0x828. */
uint32_t mspi_cq_disable(void *h) {
 return am_hal_cmdq_disable((void *)(uintptr_t)*(uint32_t *)((uint8_t *)h+0x828));
}
/* Stock termination selects the GLOBAL module slot, not the caller-local slot.
 * Does not wait or free; intentionally preserves ignored lower-level status. */
uint32_t mspi_cq_term(void *h) {
 uint32_t module=((am_hal_mspi_state_t *)h)->ui32Module;
 volatile uint32_t *slot=(volatile uint32_t *)(uintptr_t)(0x200523d8u+module*0x8d0u+0x828u);
 if (*slot) { am_hal_cmdq_term((void *)(uintptr_t)*slot,true); *slot=0; }
 return AM_HAL_STATUS_SUCCESS;
}
