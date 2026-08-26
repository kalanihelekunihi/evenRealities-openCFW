/* SPDX-License-Identifier: MIT */

/*
 * Production specialization of the maintained mpaland-derived formatter for
 * the authenticated G2 IAR DLIB printf core.  The fixed recursive address is
 * the reviewed placement of this same function in the Apollo overlay.
 */
#define OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION \
    open_cfw_runtime_iar_vsnprintf_engine
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_COUNT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_HEXFLOAT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_IAR_LENGTHS 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_RECURSE_ADDRESS 0x007F7060U

#include "../../apollo_main/core_overlay/runtime_vsnprintf.c"
