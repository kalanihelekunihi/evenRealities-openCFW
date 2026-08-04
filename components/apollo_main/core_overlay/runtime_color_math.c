/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacements for the G2 2.2.6.10 packed-color helpers:
 *   0x00482E4C...0x00482ED3  alpha-weighted three-lane mix
 *   0x00482ED4...0x00482EF5  packed-color brightness
 *
 * Packed words use three color bytes at bits 7:0, 15:8, and 23:16, followed
 * by alpha at bits 31:24. The mix takes its controlling alpha and source
 * lanes from the first word but always retains the second word's alpha.
 */

typedef unsigned int open_cfw_runtime_color_word;

_Static_assert(
    sizeof(open_cfw_runtime_color_word) == 4U,
    "runtime color word width changed"
);

static unsigned int open_cfw_runtime_color_lane(
    open_cfw_runtime_color_word color,
    unsigned int shift
)
{
    return (color >> shift) & 0xFFU;
}

static unsigned int open_cfw_runtime_color_mix_lane(
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

__attribute__((used, noinline))
open_cfw_runtime_color_word open_cfw_runtime_color_mix_alpha(
    open_cfw_runtime_color_word source,
    open_cfw_runtime_color_word destination
)
{
    unsigned int alpha = open_cfw_runtime_color_lane(source, 24U);
    open_cfw_runtime_color_word result;

    if (alpha >= 253U) {
        return (
            (source & 0x00FFFFFFU)
            | (destination & 0xFF000000U)
        );
    }
    if (alpha < 3U) {
        return destination;
    }

    result = destination & 0xFF000000U;
    result |= open_cfw_runtime_color_mix_lane(
        open_cfw_runtime_color_lane(source, 0U),
        open_cfw_runtime_color_lane(destination, 0U),
        alpha
    );
    result |= open_cfw_runtime_color_mix_lane(
        open_cfw_runtime_color_lane(source, 8U),
        open_cfw_runtime_color_lane(destination, 8U),
        alpha
    ) << 8U;
    result |= open_cfw_runtime_color_mix_lane(
        open_cfw_runtime_color_lane(source, 16U),
        open_cfw_runtime_color_lane(destination, 16U),
        alpha
    ) << 16U;
    return result;
}

__attribute__((used, noinline))
open_cfw_runtime_color_word open_cfw_runtime_color_brightness(
    open_cfw_runtime_color_word color
)
{
    unsigned int weighted =
        open_cfw_runtime_color_lane(color, 0U) * 4U
        + open_cfw_runtime_color_lane(color, 8U)
        + open_cfw_runtime_color_lane(color, 16U) * 3U;

    return (unsigned char)(weighted >> 3U);
}
