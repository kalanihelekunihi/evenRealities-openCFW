/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Production bindings for the clean-room ARC runtime implementation.  The
 * generic implementation remains independently host-testable; these aliases
 * give the production provider unambiguous symbols without duplicating it.
 */

#define open_cfw_em9305_metaware_memmove_candidate \
    open_cfw_em9305_metaware_memmove
#define open_cfw_em9305_metaware_memcpy_candidate \
    open_cfw_em9305_metaware_memcpy
#define open_cfw_em9305_metaware_memset_candidate \
    open_cfw_em9305_metaware_memset
#define open_cfw_em9305_metaware_udiv64_candidate \
    open_cfw_em9305_metaware_udiv64
#define open_cfw_em9305_metaware_sdiv64_candidate \
    open_cfw_em9305_metaware_sdiv64
#define open_cfw_em9305_metaware_shift_left64_candidate \
    open_cfw_em9305_metaware_shift_left64
#define open_cfw_em9305_metaware_shift_right64_candidate \
    open_cfw_em9305_metaware_shift_right64
#define open_cfw_em9305_metaware_stack_guard_candidate \
    open_cfw_em9305_metaware_stack_guard_with_policy

#include "../../shared/em9305/runtime_metaware_helpers_candidate.c"
#include "runtime_metaware.h"

#ifdef OPEN_CFW_EM9305_HOST_TEST
uintptr_t open_cfw_em9305_host_stack_pointer;
uint32_t open_cfw_em9305_host_stack_trap_count;

static uintptr_t open_cfw_em9305_current_stack_pointer(void)
{
    return open_cfw_em9305_host_stack_pointer;
}

static void open_cfw_em9305_stack_trap(void)
{
    ++open_cfw_em9305_host_stack_trap_count;
}
#else
static uintptr_t open_cfw_em9305_current_stack_pointer(void)
{
    register uintptr_t stack_pointer __asm__("sp");
    return stack_pointer;
}

__attribute__((noreturn))
static void open_cfw_em9305_stack_trap(void)
{
    __builtin_trap();
}
#endif

void open_cfw_em9305_metaware_stack_guard(void)
{
    if (open_cfw_em9305_metaware_stack_pointer_in_bounds(
            open_cfw_em9305_current_stack_pointer(),
            OPEN_CFW_EM9305_STACK_LIMIT_LOW,
            OPEN_CFW_EM9305_STACK_LIMIT_HIGH) == 0u) {
        open_cfw_em9305_stack_trap();
    }
}
