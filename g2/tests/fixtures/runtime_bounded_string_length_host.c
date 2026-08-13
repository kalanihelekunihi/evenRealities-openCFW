/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the source-owned bounded string-length library leaf.
 */

#include "../../components/apollo_main/core_overlay/runtime_bounded_string_length.c"

unsigned int open_cfw_test_bounded_string_length_execute(
    const unsigned char *string,
    unsigned int maximum_length
)
{
    return open_cfw_runtime_bounded_string_length(
        (const char *)(const void *)string,
        maximum_length
    );
}

unsigned int open_cfw_test_bounded_string_length_null(
    unsigned int maximum_length
)
{
    return open_cfw_runtime_bounded_string_length(
        (const char *)0,
        maximum_length
    );
}

unsigned int open_cfw_test_bounded_string_length_zero_maximum_no_load(void)
{
    return open_cfw_runtime_bounded_string_length(
        (const char *)(__UINTPTR_TYPE__)1U,
        0U
    );
}
