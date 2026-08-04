/*
 * SPDX-License-Identifier: BSD-2-Clause
 *
 * Isolated, non-production G2 ABI adapter for the authenticated upstream
 * LZ4 v1.10.0 LZ4_decompress_safe implementation.  The pristine upstream
 * implementation and license are retained under third_party/lz4.
 *
 * This path is intentionally absent from every production overlay and
 * manifest.  It exists to qualify direct upstream reuse before promotion.
 */

#include "../../third_party/lz4/lz4.h"

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
