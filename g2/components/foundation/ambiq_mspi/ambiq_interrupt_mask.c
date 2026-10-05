//*****************************************************************************
//
//! @file am_hal_interrupt.c
//!
//! @brief Helper functions supporting interrupts and NVIC operation.
//!
//! @addtogroup interrupt_ap510 Interrupt - ARM NVIC support functions
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides helper functions for supporting interrupts
//!          and NVIC (Nested Vectored Interrupt Controller) operations on
//!          Apollo5 devices. It supports interrupt enable/disable, master
//!          interrupt control, and interrupt state management for system
//!          interrupt handling and control.
//!
//! @section hal_interrupt_features Key Features
//!
//! 1. @b Master @b Interrupt @b Control: Global interrupt enable/disable functionality.
//! 2. @b NVIC @b Support: ARM NVIC interrupt controller support.
//! 3. @b Interrupt @b State: Interrupt state management and control.
//! 4. @b Compiler @b Support: Multi-compiler support for interrupt operations.
//! 5. @b Priority @b Management: Interrupt priority handling and control.
//!
//! @section hal_interrupt_functionality Functionality
//!
//! - Enable and disable master interrupts globally
//! - Control interrupt state and priority
//! - Support NVIC interrupt operations
//! - Handle interrupt enable/disable operations
//! - Provide compiler-specific interrupt implementations
//!
//! @section hal_interrupt_usage Usage
//!
//! 1. Enable master interrupts using am_hal_interrupt_master_enable()
//! 2. Disable master interrupts using am_hal_interrupt_master_disable()
//! 3. Set interrupt state as needed
//! 4. Handle interrupt operations and state management
//! 5. Control interrupt priorities and NVIC operations
//!
//! @section hal_interrupt_configuration Configuration
//!
//! - @b Master @b Interrupt: Configure global interrupt enable/disable
//! - @b NVIC @b Settings: Set up NVIC interrupt controller parameters
//! - @b Priority @b Levels: Configure interrupt priority levels
//! - @b Compiler: Set up compiler-specific interrupt implementations
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

#include "ambiq_interrupt_mask.h"
/* This provider is selected only by the architectural-mask simulator profile.
 * Privileged execution is a caller precondition. Physical IRQ delivery is not
 * supplied by the callable module. */
#ifdef OPENCFW_REAL_CRITICAL
uint32_t __attribute__((naked))
am_hal_interrupt_master_disable(void)
{
    __asm("    mrs     r0, PRIMASK");
    __asm("    cpsid i");
    __asm("    bx lr");
}
/* Alias adapts the recovered CMDQ subset's existing provider name; no wrapper
 * or alternate instructions. */
uint32_t opencfw_cmdq_critical_enter(void)
 __attribute__((alias("am_hal_interrupt_master_disable")));
#endif
