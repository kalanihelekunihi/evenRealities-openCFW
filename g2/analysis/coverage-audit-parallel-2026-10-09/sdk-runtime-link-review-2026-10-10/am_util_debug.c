//*****************************************************************************
//
//! @file am_util_debug.c
//!
//! @brief Debug and Diagnostic Utility Functions
//!
//! @addtogroup debug_utils Debug Utility Functions
//! @ingroup utils
//! @{
//!
//! Purpose: This module provides debug and diagnostic utility functions
//!          for development and troubleshooting across Ambiq Micro devices.
//!          It enables printf-style debugging, ITM/SWO trace support, and
//!          diagnostic features for monitoring system behavior and debugging
//!          application code.
//!
//! @section utils_debug_features Key Features
//!
//! 1. @b Printf @b Support: Debug message output capabilities.
//! 2. @b ITM/SWO: Trace and debug interface support.
//! 3. @b Diagnostics: System monitoring and analysis.
//! 4. @b Error @b Tracking: Debug error logging and reporting.
//! 5. @b Performance: Debug impact control options.
//!
//! @section utils_debug_functionality Functionality
//!
//! - Initialize debug interfaces
//! - Output debug messages
//! - Configure trace settings
//! - Monitor system behavior
//! - Track error conditions
//!
//! @section utils_debug_usage Usage
//!
//! 1. Initialize debug with am_util_debug_init()
//! 2. Configure output options
//! 3. Use debug functions as needed
//! 4. Monitor system state
//!
//! @section utils_debug_configuration Configuration
//!
//! - Set up debug interface options
//! - Configure trace parameters
//! - Define error handling behavior
//! - Set performance impact limits
//
//*****************************************************************************

//*****************************************************************************
//
// Copyright (c) 2026, Ambiq Micro, Inc.
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
// Third party software included in this distribution is subject to the
// additional license terms as defined in the /docs/licenses directory.
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
// This is part of revision release_sdk5p2p0-66487dd10 of the AmbiqSuite Development Package.
//
//*****************************************************************************

#include "am_util_debug.h"

//
// Include a dummy function just to avoid the pedantic error, "ISO C forbids
// an empty translation unit".
//
void
am_util_debug_avoidpedanticerror(void)
{
}

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************

