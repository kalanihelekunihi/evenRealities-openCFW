/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Source replacement for the G2 2.2.6.10 two-layer packed-alpha composite
 * routine at 0x00482EF6...0x00482F71.
 *
 * Each word is little-endian BGRA: blue in bits 7:0, green in 15:8, red in
 * 23:16, and alpha in 31:24. The first word is the foreground and the second
 * is the background.
 */

typedef unsigned int open_cfw_runtime_color_over32_word;

_Static_assert(
    sizeof(open_cfw_runtime_color_over32_word) == 4U,
    "runtime color-over word width changed"
);

#ifndef OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA
typedef open_cfw_runtime_color_over32_word
(*open_cfw_runtime_color_over32_mix_alpha_fn)(
    open_cfw_runtime_color_over32_word,
    open_cfw_runtime_color_over32_word
);
#define OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA(foreground, background) \
    (((open_cfw_runtime_color_over32_mix_alpha_fn) \
        (__UINTPTR_TYPE__)0x00482E4DU)( \
            (foreground), \
            (background) \
        ))
#endif

static unsigned int open_cfw_runtime_color_over32_alpha(
    open_cfw_runtime_color_over32_word color
)
{
    return color >> 24U;
}

static open_cfw_runtime_color_over32_word
open_cfw_runtime_color_over32_replace_alpha(
    open_cfw_runtime_color_over32_word color,
    unsigned int alpha
)
{
    return (
        (color & 0x00FFFFFFU)
        | ((open_cfw_runtime_color_over32_word)(unsigned char)alpha << 24U)
    );
}

__attribute__((used, noinline))
open_cfw_runtime_color_over32_word open_cfw_runtime_color_over32(
    open_cfw_runtime_color_over32_word foreground,
    open_cfw_runtime_color_over32_word background
)
{
    unsigned int foreground_alpha =
        open_cfw_runtime_color_over32_alpha(foreground);
    unsigned int background_alpha;
    unsigned int composite_alpha;
    unsigned int ratio;
    open_cfw_runtime_color_over32_word result;

    if (foreground_alpha >= 253U) {
        return foreground;
    }

    background_alpha = open_cfw_runtime_color_over32_alpha(background);
    if (background_alpha < 3U) {
        return foreground;
    }
    if (foreground_alpha < 3U) {
        return background;
    }
    if (background_alpha == 255U) {
        return OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA(
            foreground,
            background
        );
    }

    composite_alpha = 255U - (
        (
            (255U - foreground_alpha)
            * (255U - background_alpha)
        ) >> 8U
    );
    ratio = (foreground_alpha * 255U) / composite_alpha;
    foreground = open_cfw_runtime_color_over32_replace_alpha(
        foreground,
        ratio
    );
    result = OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA(
        foreground,
        background
    );
    result = open_cfw_runtime_color_over32_replace_alpha(
        result,
        composite_alpha
    );
    return result;
}

#undef OPEN_CFW_RUNTIME_COLOR_OVER32_MIX_ALPHA
