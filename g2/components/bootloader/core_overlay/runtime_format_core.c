/* SPDX-License-Identifier: MIT */

/*
 * Bootloader binding for the clean-room IAR logging formatter core shared
 * with the Apollo application image.  The two stock 2.2.6.10 bodies have
 * the same argument-cursor and conversion contract; only their helper
 * addresses and CRLF-control byte differ.
 */

#define open_cfw_log_decimal_digits open_cfw_bootloader_udec_digits
#define open_cfw_log_signed_decimal_digits open_cfw_bootloader_sdec_digits
#define open_cfw_log_hex_digits open_cfw_bootloader_hex_digits
#define open_cfw_log_parse_integer open_cfw_bootloader_parse_dec
#define open_cfw_log_decimal_write open_cfw_bootloader_u64_to_dec
#define open_cfw_log_hex_write open_cfw_bootloader_u64_to_hex
#define open_cfw_log_string_length open_cfw_bootloader_nullable_strlen
#define open_cfw_log_padding_write open_cfw_bootloader_repeat_char
#define open_cfw_log_format_core open_cfw_bootloader_format_core

#ifndef OPEN_CFW_LOG_CORE_CRLF_ENABLED
#define OPEN_CFW_LOG_CORE_CRLF_ENABLED() \
    (*(volatile unsigned char *)(void *)0x200271C4U)
#endif

#ifndef OPEN_CFW_LOG_CORE_FLOAT_WRITE
#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_BOOTLOADER_FORMAT_FLOAT_ABI \
    __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_BOOTLOADER_FORMAT_FLOAT_ABI
#endif
typedef int OPEN_CFW_BOOTLOADER_FORMAT_FLOAT_ABI
    open_cfw_bootloader_float_to_fixed_signature(
        char *output,
        int precision,
        float value
    );
extern int OPEN_CFW_BOOTLOADER_FORMAT_FLOAT_ABI
open_cfw_bootloader_float_to_fixed(
    char *output,
    int precision,
    float value
);

#define OPEN_CFW_LOG_CORE_FLOAT_WRITE(output, precision, value) \
    (((open_cfw_bootloader_float_to_fixed_signature *) \
        open_cfw_bootloader_float_to_fixed)( \
            (output), \
            (int)(precision), \
            (value) \
        ))
#endif

#include "../../apollo_main/core_overlay/log_format_core.c"
