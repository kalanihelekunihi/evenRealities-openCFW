/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CASE_PURE_HELPERS_H
#define OPEN_CFW_RUNTIME_CASE_PURE_HELPERS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*open_cfw_case_emit_fn)(uint8_t value, void *context);

uint64_t open_cfw_case_shift_left64(uint64_t value, uint32_t shift);
uint64_t open_cfw_case_shift_right64(uint64_t value, uint32_t shift);
bool open_cfw_case_finalize_length_checksum(uint8_t *frame, size_t length);
uint8_t open_cfw_case_hex_value(uint8_t character);
bool open_cfw_case_starts_with_de(const char *text);
size_t open_cfw_case_emit_left_padding(int32_t count, uint32_t flags,
                                       open_cfw_case_emit_fn emit,
                                       void *context);
size_t open_cfw_case_emit_right_padding(int32_t count, uint32_t flags,
                                        open_cfw_case_emit_fn emit,
                                        void *context);

#ifdef __cplusplus
}
#endif

#endif
