/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL RGB888 color-mix
 * routine at 0x00482DD8...0x00482E4B.
 *
 * The machine ABI passes the three-byte first and second colors in r0 and
 * r1 and the opacity in r2. Color byte order is blue, green, red. The
 * opacity is explicitly reduced to its low byte before each channel uses
 * it. A three-byte result is returned in r0 under AAPCS; bits 31:24 are
 * aggregate padding and are intentionally unspecified.
 *
 * The stock implementation writes only bytes 0, 1, and 2 of a four-byte
 * stack return slot, then loads the complete word. Its high return byte is
 * therefore stale stack padding rather than a semantic result.
 */

typedef unsigned int open_cfw_runtime_color_mix_word;

struct open_cfw_runtime_color_mix_value {
    unsigned char blue;
    unsigned char green;
    unsigned char red;
};

_Static_assert(
    sizeof(open_cfw_runtime_color_mix_word) == 4U,
    "color-mix word width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_color_mix_value) == 3U,
    "color-mix RGB888 size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        blue
    ) == 0U,
    "color-mix blue offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        green
    ) == 1U,
    "color-mix green offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        red
    ) == 2U,
    "color-mix red offset changed"
);

static unsigned char open_cfw_runtime_color_mix_channel(
    unsigned char first,
    unsigned char second,
    open_cfw_runtime_color_mix_word opacity
)
{
    open_cfw_runtime_color_mix_word mix = (unsigned char)opacity;
    open_cfw_runtime_color_mix_word inverse = 255U - mix;
    open_cfw_runtime_color_mix_word weighted;

    weighted = (open_cfw_runtime_color_mix_word)second * inverse;
    weighted += (open_cfw_runtime_color_mix_word)first * mix;
    return (unsigned char)((weighted * 0x8081U) >> 23U);
}

__attribute__((used, noinline))
struct open_cfw_runtime_color_mix_value open_cfw_runtime_color_mix(
    struct open_cfw_runtime_color_mix_value first,
    struct open_cfw_runtime_color_mix_value second,
    open_cfw_runtime_color_mix_word opacity
)
{
    struct open_cfw_runtime_color_mix_value result;

    result.red = open_cfw_runtime_color_mix_channel(
        first.red,
        second.red,
        opacity
    );
    result.green = open_cfw_runtime_color_mix_channel(
        first.green,
        second.green,
        opacity
    );
    result.blue = open_cfw_runtime_color_mix_channel(
        first.blue,
        second.blue,
        opacity
    );
    return result;
}
