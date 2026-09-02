/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bounded floating multiplier encoder at
 * bootloader address 0x00426EAC.
 */

typedef __UINT8_TYPE__ open_cfw_float_multiplier_u8;
typedef __UINT16_TYPE__ open_cfw_float_multiplier_u16;
typedef __UINT32_TYPE__ open_cfw_float_multiplier_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_floorf_427c90(float value);
extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_fmodf_427ccc(float value, float modulus);
extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_roundf_427d98(float value);
extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_ceilf_427dd0(float value);

OPEN_CFW_AAPCS_VFP __attribute__((used, noinline))
open_cfw_float_multiplier_u32 open_cfw_bootloader_float_multiplier_426eac(
    open_cfw_float_multiplier_u8 *scale_output,
    open_cfw_float_multiplier_u16 *integer_output,
    open_cfw_float_multiplier_u32 *fraction_output,
    float first,
    float second)
{
    float ratio = second / first;
    float scale_value = open_cfw_bootloader_ceilf_427dd0(
        10.0f / ratio);
    open_cfw_float_multiplier_u32 scale;
    float product;
    float integer_value;
    open_cfw_float_multiplier_u32 fraction;
    open_cfw_float_multiplier_u32 integer;

    if ((scale_value < 0x1p-23f)
        || (scale_value >= 0x1.f80002p+5f)) {
        return 0U;
    }

    scale = (open_cfw_float_multiplier_u32)scale_value;
    product = (float)scale * ratio;
    fraction = (open_cfw_float_multiplier_u32)
        open_cfw_bootloader_roundf_427d98(
            open_cfw_bootloader_fmodf_427ccc(product, 1.0f)
            * 0x1p+24f);

    integer_value = open_cfw_bootloader_floorf_427c90(product);
    if ((integer_value < 10.0f)
        || (integer_value >= 0x1.800002p+6f)) {
        return 0U;
    }
    integer = (open_cfw_float_multiplier_u32)
        open_cfw_bootloader_floorf_427c90(product);

    *scale_output = (open_cfw_float_multiplier_u8)scale;
    *integer_output = (open_cfw_float_multiplier_u16)integer;
    *fraction_output = fraction;
    return 1U;
}
