/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the floating encoding selector at
 * bootloader address 0x00426F6C.
 */

typedef __UINT8_TYPE__ open_cfw_float_select_u8;
typedef __UINT16_TYPE__ open_cfw_float_select_u16;
typedef __UINT32_TYPE__ open_cfw_float_select_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

typedef struct open_cfw_float_select_output {
    open_cfw_float_select_u8 reserved_0;
    open_cfw_float_select_u8 high_rate;
    open_cfw_float_select_u8 ratio_encoding;
    open_cfw_float_select_u8 scale;
    open_cfw_float_select_u8 reserved_4[2];
    open_cfw_float_select_u16 integer;
    open_cfw_float_select_u32 fraction;
} open_cfw_float_select_output;

extern OPEN_CFW_AAPCS_VFP open_cfw_float_select_u32
open_cfw_bootloader_float_ratio_426db4(
    open_cfw_float_select_u8 *first_ratio,
    open_cfw_float_select_u16 *second_ratio,
    float first,
    float second);

extern OPEN_CFW_AAPCS_VFP open_cfw_float_select_u32
open_cfw_bootloader_float_multiplier_426eac(
    open_cfw_float_select_u8 *scale_output,
    open_cfw_float_select_u16 *integer_output,
    open_cfw_float_select_u32 *fraction_output,
    float first,
    float second);

OPEN_CFW_AAPCS_VFP __attribute__((used, noinline))
open_cfw_float_select_u32 open_cfw_bootloader_float_encoding_select_426f6c(
    open_cfw_float_select_output *output,
    float first,
    float second)
{
    open_cfw_float_select_u8 scale = 0U;
    open_cfw_float_select_u16 integer = 0U;
    open_cfw_float_select_u32 fraction = 0U;
    open_cfw_float_select_u32 ratio_encoding;
    open_cfw_float_select_u32 valid;

    if (output == (open_cfw_float_select_output *)0) {
        return 6U;
    }
    if ((second < 60.0f) || (0x1.e00002p+9f <= second)) {
        return 5U;
    }

    ratio_encoding = open_cfw_bootloader_float_ratio_426db4(
        &scale, &integer, first, second);
    valid = ratio_encoding;
    if (valid == 0U) {
        valid = open_cfw_bootloader_float_multiplier_426eac(
            &scale, &integer, &fraction, first, second);
    }
    if (valid == 0U) {
        return 1U;
    }

    output->high_rate = (open_cfw_float_select_u8)(second >= 240.0f);
    output->ratio_encoding = (open_cfw_float_select_u8)(ratio_encoding != 0U);
    output->scale = scale;
    output->integer = integer;
    output->fraction = fraction;
    return 0U;
}
