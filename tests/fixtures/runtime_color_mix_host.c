/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host adapter for the source-owned G2 RGB888 color-mix routine.
 */

#include "../../components/apollo_main/core_overlay/runtime_color_mix.c"

unsigned int open_cfw_test_runtime_color_mix_execute(
    unsigned int first,
    unsigned int second,
    unsigned int opacity,
    unsigned int padding_carrier
)
{
    struct open_cfw_runtime_color_mix_value first_color;
    struct open_cfw_runtime_color_mix_value second_color;
    struct open_cfw_runtime_color_mix_value result;
    unsigned int packed = padding_carrier & 0xFF000000U;

    first_color.blue = (unsigned char)first;
    first_color.green = (unsigned char)(first >> 8U);
    first_color.red = (unsigned char)(first >> 16U);
    second_color.blue = (unsigned char)second;
    second_color.green = (unsigned char)(second >> 8U);
    second_color.red = (unsigned char)(second >> 16U);

    result = open_cfw_runtime_color_mix(
        first_color,
        second_color,
        opacity
    );
    packed |= (unsigned int)result.blue;
    packed |= (unsigned int)result.green << 8U;
    packed |= (unsigned int)result.red << 16U;
    return packed;
}

unsigned int open_cfw_test_runtime_color_mix_size(void)
{
    return sizeof(struct open_cfw_runtime_color_mix_value);
}

unsigned int open_cfw_test_runtime_color_mix_blue_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        blue
    );
}

unsigned int open_cfw_test_runtime_color_mix_green_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        green
    );
}

unsigned int open_cfw_test_runtime_color_mix_red_offset(void)
{
    return __builtin_offsetof(
        struct open_cfw_runtime_color_mix_value,
        red
    );
}
