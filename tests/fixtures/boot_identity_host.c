/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the boot reset-status and firmware-version helpers.
 */

unsigned int open_cfw_test_boot_identity_status_word;
unsigned int open_cfw_test_boot_identity_status_result;
unsigned int open_cfw_test_boot_identity_clear_calls;
unsigned int open_cfw_test_boot_identity_clear_length;
unsigned int open_cfw_test_boot_identity_status_calls;
unsigned int open_cfw_test_boot_identity_observed_nonzero;
unsigned int open_cfw_test_boot_identity_trace[4];
unsigned int open_cfw_test_boot_identity_trace_count;
char open_cfw_test_boot_identity_version[128];

static void open_cfw_test_boot_identity_record(unsigned int event)
{
    open_cfw_test_boot_identity_trace[
        open_cfw_test_boot_identity_trace_count
    ] = event;
    open_cfw_test_boot_identity_trace_count += 1U;
}

static void open_cfw_test_boot_identity_clear(
    unsigned char *destination,
    unsigned int length
)
{
    unsigned int index;

    open_cfw_test_boot_identity_clear_calls += 1U;
    open_cfw_test_boot_identity_clear_length = length;
    open_cfw_test_boot_identity_record(1U);
    for (index = 0U; index < length; ++index) {
        destination[index] = 0U;
    }
}

static unsigned int open_cfw_test_boot_identity_status_get(void *output)
{
    unsigned char *status = (unsigned char *)output;
    unsigned int index;

    open_cfw_test_boot_identity_status_calls += 1U;
    open_cfw_test_boot_identity_record(2U);
    open_cfw_test_boot_identity_observed_nonzero = 0U;
    for (index = 0U; index < 16U; ++index) {
        open_cfw_test_boot_identity_observed_nonzero |= status[index];
    }
    status[0] = (unsigned char)open_cfw_test_boot_identity_status_word;
    status[1] = (unsigned char)(
        open_cfw_test_boot_identity_status_word >> 8U
    );
    for (index = 2U; index < 16U; ++index) {
        status[index] = (unsigned char)(0x80U + index);
    }
    return open_cfw_test_boot_identity_status_result;
}

#define OPEN_CFW_BOOT_RESET_STATUS_GET(status) \
    open_cfw_test_boot_identity_status_get(status)
#define OPEN_CFW_BOOT_IDENTITY_CLEAR(destination, length) \
    open_cfw_test_boot_identity_clear((destination), (length))
#define OPEN_CFW_FIRMWARE_VERSION_STRING \
    open_cfw_test_boot_identity_version

#include "../../components/apollo_main/core_overlay/boot_identity.c"
