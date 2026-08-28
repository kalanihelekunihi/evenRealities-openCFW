/* SPDX-License-Identifier: MIT */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_NUMERIC_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_NUMERIC_H

#include <stdint.h>

uint32_t open_cfw_bootloader_udec_digits(uint64_t value);
uint32_t open_cfw_bootloader_sdec_digits(int64_t value);
uint32_t open_cfw_bootloader_hex_digits(uint64_t value);
int32_t open_cfw_bootloader_parse_dec(const char *text, uint32_t *consumed);
uint32_t open_cfw_bootloader_u64_to_dec(uint64_t value, char *output);
uint32_t open_cfw_bootloader_u64_to_hex(
    uint64_t value,
    char *output,
    uint32_t lowercase
);
uint32_t open_cfw_bootloader_nullable_strlen(const char *text);
uint32_t open_cfw_bootloader_repeat_char(
    char *output,
    uint32_t character,
    int32_t count
);

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BOOTLOADER_FLOAT_ABI __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_BOOTLOADER_FLOAT_ABI
#endif

OPEN_CFW_BOOTLOADER_FLOAT_ABI
int32_t open_cfw_bootloader_float_to_fixed(
    char *output,
    int32_t precision,
    float value
);

uint32_t open_cfw_bootloader_format_core(
    char *output,
    const char *format,
    void *argument_cursor
);

uint32_t open_cfw_bootloader_log_dispatch(const char *format, ...);

#endif
