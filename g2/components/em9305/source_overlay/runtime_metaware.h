/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 OpenCFW Contributors
 */

#ifndef OPEN_CFW_EM9305_RUNTIME_METAWARE_H
#define OPEN_CFW_EM9305_RUNTIME_METAWARE_H

#include <stddef.h>
#include <stdint.h>

void *open_cfw_em9305_metaware_memmove(
    void *destination, const void *source, size_t length
);
void *open_cfw_em9305_metaware_memcpy(
    void *destination, const void *source, size_t length
);
void *open_cfw_em9305_metaware_memset(
    void *destination, int value, size_t length
);
uint64_t open_cfw_em9305_metaware_udiv64(uint64_t dividend, uint64_t divisor);
int64_t open_cfw_em9305_metaware_sdiv64(int64_t dividend, int64_t divisor);
uint64_t open_cfw_em9305_metaware_shift_left64(uint64_t value, uint32_t count);
uint64_t open_cfw_em9305_metaware_shift_right64(uint64_t value, uint32_t count);
uint32_t open_cfw_em9305_metaware_stack_pointer_in_bounds(
    uintptr_t stack_pointer, uintptr_t low_limit, uintptr_t high_limit
);
void open_cfw_em9305_metaware_stack_guard(void);

#ifdef OPEN_CFW_EM9305_HOST_TEST
extern uintptr_t open_cfw_em9305_host_stack_pointer;
extern uint32_t open_cfw_em9305_host_stack_trap_count;
#endif

#endif
