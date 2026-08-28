/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter for the source-owned G2 packed-color arithmetic helpers.
 */

#include "../../components/apollo_main/core_overlay/runtime_color_math.c"

unsigned int open_cfw_test_runtime_color_mix_alpha(
    unsigned int source,
    unsigned int destination
)
{
    return open_cfw_runtime_color_mix_alpha(source, destination);
}

unsigned int open_cfw_test_runtime_color_brightness(unsigned int color)
{
    return open_cfw_runtime_color_brightness(color);
}
