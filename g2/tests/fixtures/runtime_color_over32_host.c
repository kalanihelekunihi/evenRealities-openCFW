/*
 * SPDX-License-Identifier: MIT
 *
 * Host adapter and dependency trace for the packed two-layer alpha composite.
 */

unsigned int open_cfw_test_runtime_color_over32_mix_calls;
unsigned int open_cfw_test_runtime_color_over32_mix_foreground;
unsigned int open_cfw_test_runtime_color_over32_mix_background;
unsigned int open_cfw_test_runtime_color_over32_mix_result;

static unsigned int open_cfw_test_runtime_color_over32_lane(
    unsigned int color,
    unsigned int shift
)
{
    return (color >> shift) & 0xFFU;
}

static unsigned int open_cfw_test_runtime_color_over32_mix_lane(
    unsigned int source,
    unsigned int destination,
    unsigned int alpha
)
{
    return (
        alpha * source
        + (255U - alpha) * destination
    ) >> 8U;
}

static unsigned int open_cfw_test_runtime_color_over32_mix_alpha(
    unsigned int foreground,
    unsigned int background
)
{
    unsigned int alpha =
        open_cfw_test_runtime_color_over32_lane(foreground, 24U);
    unsigned int result;

    open_cfw_test_runtime_color_over32_mix_calls += 1U;
    open_cfw_test_runtime_color_over32_mix_foreground = foreground;
    open_cfw_test_runtime_color_over32_mix_background = background;

    if (alpha >= 253U) {
        result = (
            (foreground & 0x00FFFFFFU)
            | (background & 0xFF000000U)
        );
    } else if (alpha < 3U) {
        result = background;
    } else {
        result = background & 0xFF000000U;
        result |= open_cfw_test_runtime_color_over32_mix_lane(
            open_cfw_test_runtime_color_over32_lane(foreground, 0U),
            open_cfw_test_runtime_color_over32_lane(background, 0U),
            alpha
        );
        result |= open_cfw_test_runtime_color_over32_mix_lane(
            open_cfw_test_runtime_color_over32_lane(foreground, 8U),
            open_cfw_test_runtime_color_over32_lane(background, 8U),
            alpha
        ) << 8U;
        result |= open_cfw_test_runtime_color_over32_mix_lane(
            open_cfw_test_runtime_color_over32_lane(foreground, 16U),
            open_cfw_test_runtime_color_over32_lane(background, 16U),
            alpha
        ) << 16U;
    }
    open_cfw_test_runtime_color_over32_mix_result = result;
    return result;
}

#define OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA(foreground, background) \
    open_cfw_test_runtime_color_over32_mix_alpha( \
        (foreground), \
        (background) \
    )

#include "../../components/apollo_main/core_overlay/runtime_color_over32.c"

void open_cfw_test_runtime_color_over32_reset(void)
{
    open_cfw_test_runtime_color_over32_mix_calls = 0U;
    open_cfw_test_runtime_color_over32_mix_foreground = 0U;
    open_cfw_test_runtime_color_over32_mix_background = 0U;
    open_cfw_test_runtime_color_over32_mix_result = 0U;
}
