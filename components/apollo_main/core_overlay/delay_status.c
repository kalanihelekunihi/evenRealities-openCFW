/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Bounded Apollo510 status-wait helpers adapted from AmbiqSuite SDK 5.1.0
 * and the reviewed G2 2.2.6.10 stock functions at
 * 0x004807FC...0x00480869.
 */

typedef __UINTPTR_TYPE__ open_cfw_delay_status_uintptr;

#define OPEN_CFW_DELAY_STATUS_SUCCESS 0U
#define OPEN_CFW_DELAY_STATUS_TIMEOUT 4U
#define OPEN_CFW_DELAY_STATUS_DELAY_US_ENTRY 0x004807A1U

#ifndef OPEN_CFW_DELAY_STATUS_READ32
#define OPEN_CFW_DELAY_STATUS_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_delay_status_uintptr)(address))
#endif

#ifndef OPEN_CFW_DELAY_STATUS_DELAY_US
typedef void (*open_cfw_delay_status_delay_function)(unsigned int);
#define OPEN_CFW_DELAY_STATUS_DELAY_US(microseconds) \
    (((open_cfw_delay_status_delay_function) \
        (open_cfw_delay_status_uintptr) \
        OPEN_CFW_DELAY_STATUS_DELAY_US_ENTRY)((microseconds)))
#endif

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_delay_us_status_change at 0x004807FC...0x00480825.
 */
__attribute__((used, noinline))
unsigned int open_cfw_delay_us_status_change(
    unsigned int maximum_delay_microseconds,
    unsigned int address,
    unsigned int mask,
    unsigned int value
)
{
    for (;;) {
        if ((OPEN_CFW_DELAY_STATUS_READ32(address) & mask) == value) {
            return OPEN_CFW_DELAY_STATUS_SUCCESS;
        }

        if (maximum_delay_microseconds-- != 0U) {
            OPEN_CFW_DELAY_STATUS_DELAY_US(1U);
        } else {
            break;
        }
    }

    return OPEN_CFW_DELAY_STATUS_TIMEOUT;
}

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_delay_us_status_check at 0x00480826...0x00480869. The fifth
 * argument is intentionally byte-typed: the stock body truncates the
 * stack-passed value before choosing equality or inequality mode.
 */
__attribute__((used, noinline))
unsigned int open_cfw_delay_us_status_check(
    unsigned int maximum_delay_microseconds,
    unsigned int address,
    unsigned int mask,
    unsigned int value,
    unsigned char is_equal
)
{
    for (;;) {
        unsigned int masked =
            OPEN_CFW_DELAY_STATUS_READ32(address) & mask;

        if (
            (is_equal != 0U && masked == value)
            || (is_equal == 0U && masked != value)
        ) {
            return OPEN_CFW_DELAY_STATUS_SUCCESS;
        }

        if (maximum_delay_microseconds-- != 0U) {
            OPEN_CFW_DELAY_STATUS_DELAY_US(1U);
        } else {
            break;
        }
    }

    return OPEN_CFW_DELAY_STATUS_TIMEOUT;
}

#undef OPEN_CFW_DELAY_STATUS_DELAY_US
#undef OPEN_CFW_DELAY_STATUS_READ32

