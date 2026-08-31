/* SPDX-License-Identifier: MIT */

/*
 * Production specialization of the maintained mpaland-derived formatter for
 * the authenticated G2 IAR DLIB printf core.  Recursive %PV/%pV formatting
 * calls this same function directly, so the compiler preserves a relative
 * self-call instead of embedding a placement-specific executable address.
 */
#define OPEN_CFW_RUNTIME_VSNPRINTF_FUNCTION \
    open_cfw_runtime_iar_vsnprintf_engine
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_COUNT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_HEXFLOAT 1
#define OPEN_CFW_RUNTIME_VSNPRINTF_ENABLE_IAR_LENGTHS 1

#include "../../apollo_main/core_overlay/runtime_vsnprintf.c"
