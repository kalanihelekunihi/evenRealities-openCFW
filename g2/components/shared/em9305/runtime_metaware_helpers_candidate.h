/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 *
 * Clean-room semantic candidates for the reconstructible EM9305 MetaWare
 * runtime islands.  These declarations do not reproduce MetaWare code.
 */

#ifndef OPEN_CFW_RUNTIME_EM9305_METAWARE_HELPERS_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EM9305_METAWARE_HELPERS_CANDIDATE_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPEN_CFW_EM9305_METAWARE_ARITH_START 0x00302664u
#define OPEN_CFW_EM9305_METAWARE_ARITH_END 0x0030299au
#define OPEN_CFW_EM9305_METAWARE_ARITH_BYTES 822u
#define OPEN_CFW_EM9305_METAWARE_MEMORY_START 0x00332fc4u
#define OPEN_CFW_EM9305_METAWARE_MEMORY_END 0x00333062u
#define OPEN_CFW_EM9305_METAWARE_MEMORY_BYTES 158u
#define OPEN_CFW_EM9305_METAWARE_TOTAL_BYTES 980u

#define OPEN_CFW_EM9305_STACK_LIMIT_LOW 0x0080e978u
#define OPEN_CFW_EM9305_STACK_LIMIT_HIGH 0x0080f978u

typedef void (*open_cfw_em9305_stack_trap_t)(void *context);

void *open_cfw_em9305_metaware_memmove_candidate(
    void *destination,
    const void *source,
    size_t length
);

void *open_cfw_em9305_metaware_memcpy_candidate(
    void *destination,
    const void *source,
    size_t length
);

void *open_cfw_em9305_metaware_memset_candidate(
    void *destination,
    int value,
    size_t length
);

uint64_t open_cfw_em9305_metaware_udiv64_candidate(
    uint64_t dividend,
    uint64_t divisor
);

int64_t open_cfw_em9305_metaware_sdiv64_candidate(
    int64_t dividend,
    int64_t divisor
);

uint64_t open_cfw_em9305_metaware_shift_left64_candidate(
    uint64_t value,
    uint32_t count
);

uint64_t open_cfw_em9305_metaware_shift_right64_candidate(
    uint64_t value,
    uint32_t count
);

uint32_t open_cfw_em9305_metaware_stack_pointer_in_bounds(
    uintptr_t stack_pointer,
    uintptr_t low_limit,
    uintptr_t high_limit
);

uint32_t open_cfw_em9305_metaware_stack_guard_candidate(
    uintptr_t stack_pointer,
    open_cfw_em9305_stack_trap_t trap,
    void *trap_context
);

#ifdef __cplusplus
}
#endif

#endif
