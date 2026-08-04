/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the source-owned bounded string-length routine.
 */

#include "../../components/apollo_main/core_overlay/runtime_bounded_string_length.c"
#include "../../components/apollo_main/core_overlay/runtime_strnlen_s.c"

unsigned int open_cfw_test_runtime_strnlen_s_execute(
    const unsigned char *string,
    unsigned int maximum_length
)
{
    return open_cfw_runtime_strnlen_s(
        (const char *)(const void *)string,
        maximum_length
    );
}

unsigned int open_cfw_test_runtime_strnlen_s_null(
    unsigned int maximum_length
)
{
    return open_cfw_runtime_strnlen_s(
        (const char *)0,
        maximum_length
    );
}

unsigned int open_cfw_test_runtime_strnlen_s_zero_maximum_no_load(void)
{
    return open_cfw_runtime_strnlen_s(
        (const char *)(__UINTPTR_TYPE__)1U,
        0U
    );
}
