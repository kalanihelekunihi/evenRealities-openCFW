/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Boot reset-status and firmware-version helpers matched to stock entries
 * 0x0047DCEC and 0x0047DD08.
 */

typedef __UINTPTR_TYPE__ open_cfw_boot_identity_uintptr;

typedef unsigned int (*open_cfw_boot_identity_status_function)(void *);

#ifndef OPEN_CFW_BOOT_RESET_STATUS_GET
#define OPEN_CFW_BOOT_RESET_STATUS_GET(status) \
    (((open_cfw_boot_identity_status_function) \
        (open_cfw_boot_identity_uintptr)0x004D3555U)((status)))
#endif

#ifndef OPEN_CFW_BOOT_IDENTITY_CLEAR
static __attribute__((always_inline)) inline void
open_cfw_boot_identity_clear_target(
    unsigned char *destination,
    unsigned int length
)
{
    unsigned int index;

    for (index = 0U; index < length; ++index) {
        destination[index] = 0U;
    }
}

#define OPEN_CFW_BOOT_IDENTITY_CLEAR(destination, length) \
    open_cfw_boot_identity_clear_target((destination), (length))
#endif

#ifndef OPEN_CFW_FIRMWARE_VERSION_STRING
#define OPEN_CFW_FIRMWARE_VERSION_STRING "2.2.6.10"
#endif

__attribute__((used, noinline))
int open_cfw_reset_status_word(void)
{
    unsigned char status[16];
    unsigned int word;

    OPEN_CFW_BOOT_IDENTITY_CLEAR(status, 16U);
    (void)OPEN_CFW_BOOT_RESET_STATUS_GET(status);
    word = (unsigned int)status[0]
        | ((unsigned int)status[1] << 8U);
    return (int)(signed short)word;
}

__attribute__((used, noinline))
unsigned int open_cfw_firmware_version_code(void)
{
    const unsigned char *cursor =
        (const unsigned char *)OPEN_CFW_FIRMWARE_VERSION_STRING;
    unsigned int components[3] = {0U, 0U, 0U};
    unsigned int count = 0U;

    while (*cursor != 0U && count < 3U) {
        unsigned int digit = (unsigned int)*cursor - (unsigned int)'0';

        if (digit < 10U) {
            unsigned int value = 0U;

            do {
                value = value * 10U + digit;
                ++cursor;
                digit = (unsigned int)*cursor - (unsigned int)'0';
            } while (digit < 10U);
            components[count] = value;
            ++count;
        }
        else {
            ++cursor;
        }
    }

    return (components[0] << 16U)
        | (components[1] << 8U)
        | components[2];
}

#undef OPEN_CFW_FIRMWARE_VERSION_STRING
#undef OPEN_CFW_BOOT_IDENTITY_CLEAR
#undef OPEN_CFW_BOOT_RESET_STATUS_GET
