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

#ifndef OPENCFW_CMDQ_H
#define OPENCFW_CMDQ_H
#include "ambiq_mspi_compat.h"
/* ARM32 view recovered from stock; no allocator or queue initializer. */
typedef struct {
 volatile uint32_t *regCQCfg, *regCQAddr, *regCurIdx, *regEndIdx, *regCQPause;
 uint32_t bitMaskCQPauseIdx;
} am_hal_cmdq_registers_t;
typedef struct {
 am_hal_handle_prefix_t prefix;
 uint32_t cmdQBufStart,cmdQBufEnd,cmdQHead,cmdQTail,cmdQNextTail,cmdQSize,curIdx,endIdx;
 const am_hal_cmdq_registers_t *pReg;
 uint32_t rawSeqStart;
} am_hal_cmdq_t;
_Static_assert(sizeof(void *)==4,"CMDQ subset requires ARM32");
_Static_assert(offsetof(am_hal_cmdq_t,pReg)==0x24,"stock CMDQ register table");
uint32_t am_hal_cmdq_disable(void *);
uint32_t am_hal_cmdq_term(void *,bool);
uint32_t opencfw_cmdq_critical_enter(void);
#endif
