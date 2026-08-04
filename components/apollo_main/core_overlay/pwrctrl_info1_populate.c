/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 INFO1 cache-population adaptation from AmbiqSuite SDK
 * 5.1.0. Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_info1_uintptr;

typedef struct open_cfw_pwrctrl_info1_registers {
    unsigned int words[32];
} open_cfw_pwrctrl_info1_registers;

_Static_assert(
    sizeof(open_cfw_pwrctrl_info1_registers) == 128U,
    "Apollo510 INFO1 cache ABI must remain 32 words"
);

#define OPEN_CFW_PWRCTRL_INFO1_REGS_DEFAULT_ADDRESS 0x20071948U
#define OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_ADDRESS 0x400201BCU
#define OPEN_CFW_PWRCTRL_INFO1_POWER_STATUS_ADDRESS 0x40021008U
#define OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_MASK (1U << 3)
#define OPEN_CFW_PWRCTRL_INFO1_OTP_POWER_STATUS_MASK (1U << 27)
#define OPEN_CFW_PWRCTRL_INFO1_READ_ENTRY 0x004D3F3DU
#define OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_INFO1_STATUS_INVALID_OPERATION 7U
#define OPEN_CFW_PWRCTRL_INFO1_GLOBAL_VALID 0x1F01600DU
#define OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT 1U
#define OPEN_CFW_PWRCTRL_INFO1_SPACE_OTP 3U
#define OPEN_CFW_PWRCTRL_INFO1_SPACE_MRAM 5U

#ifndef OPEN_CFW_PWRCTRL_INFO1_REGS_ADDRESS
#define OPEN_CFW_PWRCTRL_INFO1_REGS_ADDRESS \
    OPEN_CFW_PWRCTRL_INFO1_REGS_DEFAULT_ADDRESS
#endif

#ifndef OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER
#define OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_info1_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_INFO1_READ
typedef unsigned int (*open_cfw_pwrctrl_info1_read_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int *
);
#define OPEN_CFW_PWRCTRL_INFO1_READ( \
    info_space, word_offset, word_count, destination \
) \
    (((open_cfw_pwrctrl_info1_read_function) \
        OPEN_CFW_PWRCTRL_INFO1_READ_ENTRY)( \
            (info_space), \
            (word_offset), \
            (word_count), \
            (destination) \
        ))
#endif

static unsigned int
open_cfw_pwrctrl_info1_read_checked(
    unsigned int info_space,
    unsigned int word_offset,
    unsigned int word_count,
    unsigned int *destination
)
{
    return OPEN_CFW_PWRCTRL_INFO1_READ(
        info_space,
        word_offset,
        word_count,
        destination
    );
}

/*
 * ABI-compatible source replacement for AmbiqSuite's private
 * pwrctrl_INFO1_populate at 0x0047F954...0x0047FAB3.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_info1_populate(void)
{
    volatile open_cfw_pwrctrl_info1_registers *registers =
        (volatile open_cfw_pwrctrl_info1_registers *)
            (open_cfw_pwrctrl_info1_uintptr)
                OPEN_CFW_PWRCTRL_INFO1_REGS_ADDRESS;
    unsigned int buffer[12];
    unsigned int status;
    unsigned int index;

    if (
        (
            OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER(
                OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_ADDRESS
            ) & OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_MASK
        ) == 0U
        || (
            OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER(
                OPEN_CFW_PWRCTRL_INFO1_POWER_STATUS_ADDRESS
            ) & OPEN_CFW_PWRCTRL_INFO1_OTP_POWER_STATUS_MASK
        ) == 0U
    ) {
        return OPEN_CFW_PWRCTRL_INFO1_STATUS_INVALID_OPERATION;
    }

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_MRAM,
        0x480U,
        2U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[1] = buffer[0];
    registers->words[2] = buffer[1];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x204U,
        1U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[3] = buffer[0];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x206U,
        1U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[4] = buffer[0];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_OTP,
        0x208U,
        8U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    for (index = 0U; index < 8U; ++index) {
        registers->words[5U + index] = buffer[index];
    }

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x210U,
        1U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[13] = buffer[0];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x240U,
        3U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[14] = buffer[0];
    registers->words[15] = buffer[1];
    registers->words[16] = buffer[2];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x24AU,
        2U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[18] = buffer[0];
    registers->words[19] = buffer[1];

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x250U,
        12U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    for (index = 0U; index < 12U; ++index) {
        registers->words[20U + index] = buffer[index];
    }

    status = open_cfw_pwrctrl_info1_read_checked(
        OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT,
        0x245U,
        1U,
        buffer
    );
    if (status != OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS) {
        return status;
    }
    registers->words[17] = buffer[0];
    registers->words[0] = OPEN_CFW_PWRCTRL_INFO1_GLOBAL_VALID;

    return status;
}

#undef OPEN_CFW_PWRCTRL_INFO1_READ
#undef OPEN_CFW_PWRCTRL_INFO1_READ_REGISTER
#undef OPEN_CFW_PWRCTRL_INFO1_REGS_ADDRESS
#undef OPEN_CFW_PWRCTRL_INFO1_SPACE_MRAM
#undef OPEN_CFW_PWRCTRL_INFO1_SPACE_OTP
#undef OPEN_CFW_PWRCTRL_INFO1_SPACE_CURRENT
#undef OPEN_CFW_PWRCTRL_INFO1_GLOBAL_VALID
#undef OPEN_CFW_PWRCTRL_INFO1_STATUS_INVALID_OPERATION
#undef OPEN_CFW_PWRCTRL_INFO1_STATUS_SUCCESS
#undef OPEN_CFW_PWRCTRL_INFO1_READ_ENTRY
#undef OPEN_CFW_PWRCTRL_INFO1_OTP_POWER_STATUS_MASK
#undef OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_MASK
#undef OPEN_CFW_PWRCTRL_INFO1_POWER_STATUS_ADDRESS
#undef OPEN_CFW_PWRCTRL_INFO1_SHADOW_VALID_ADDRESS
#undef OPEN_CFW_PWRCTRL_INFO1_REGS_DEFAULT_ADDRESS
