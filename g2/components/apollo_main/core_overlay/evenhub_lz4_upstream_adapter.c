/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * G2 ABI adapters for the authenticated upstream LZ4 decompression closure.
 * The pristine BSD-2-Clause implementation is retained under third_party/lz4.
 * Build exactly one leaf per translation unit by selecting one build macro.
 */

#if defined(OPEN_CFW_LZ4_BUILD_SAFE_ADAPTER) == \
    defined(OPEN_CFW_LZ4_BUILD_MODE2_ADAPTER)
#error "select exactly one LZ4 adapter leaf"
#endif

#if defined(OPEN_CFW_LZ4_BUILD_SAFE_ADAPTER)

#include "../../../third_party/lz4/lz4.h"

__attribute__((used, noinline))
int open_cfw_lz4_decompress_safe(
    const unsigned char *input,
    unsigned char *output,
    int input_length,
    int output_capacity
)
{
    return LZ4_decompress_safe(
        (const char *)input,
        (char *)output,
        input_length,
        output_capacity
    );
}

#else

int open_cfw_lz4_decompress_safe(
    const unsigned char *input,
    unsigned char *output,
    int input_length,
    int output_capacity
);

/*
 * Active replacement for stock 0x004E0C0C...0x004E0C33. It preserves the
 * recovered EvenHub guards, argument order, and non-positive-result mapping.
 */
__attribute__((used, noinline))
unsigned int open_cfw_evenhub_mode2_decompress(
    const unsigned char *input,
    unsigned int input_length,
    unsigned char *output,
    unsigned int output_capacity
)
{
    int result;

    if (
        input == (const unsigned char *)0 ||
        input_length == 0U ||
        output == (unsigned char *)0 ||
        output_capacity == 0U
    ) {
        return 0U;
    }

    result = open_cfw_lz4_decompress_safe(
        input,
        output,
        (int)input_length,
        (int)output_capacity
    );
    return result < 1 ? 0U : (unsigned int)result;
}

#endif
