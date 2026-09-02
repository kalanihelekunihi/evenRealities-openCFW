/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bounded floating ratio encoder at
 * bootloader address 0x00426DB4.
 */

typedef __UINT8_TYPE__ open_cfw_float_ratio_u8;
typedef __UINT16_TYPE__ open_cfw_float_ratio_u16;
typedef __UINT32_TYPE__ open_cfw_float_ratio_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_float_gcd_426d48(float first, float second);
extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_fmodf_427ccc(float value, float modulus);
extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_roundf_427d98(float value);

OPEN_CFW_AAPCS_VFP __attribute__((used, noinline))
open_cfw_float_ratio_u32 open_cfw_bootloader_float_ratio_426db4(
    open_cfw_float_ratio_u8 *first_ratio,
    open_cfw_float_ratio_u16 *second_ratio,
    float first,
    float second)
{
    float divisor = open_cfw_bootloader_float_gcd_426d48(second, first);
    float normalized_first;
    float normalized_second;
    float rounded;
    open_cfw_float_ratio_u32 first_count;
    open_cfw_float_ratio_u32 second_count;

    if (divisor < 0x1p-23f) {
        return 0U;
    }

    normalized_second = second / divisor;
    normalized_first = first / divisor;

    if (!(open_cfw_bootloader_fmodf_427ccc(
              normalized_second, 1.0f) < 0x1.000002p-23f)) {
        return 0U;
    }
    rounded = open_cfw_bootloader_roundf_427d98(normalized_second);
    if (!(rounded < 0x1.e00002p+9f)) {
        return 0U;
    }
    second_count = (open_cfw_float_ratio_u32)
        open_cfw_bootloader_roundf_427d98(normalized_second);

    if (!(open_cfw_bootloader_fmodf_427ccc(
              normalized_first, 1.0f) < 0x1.000002p-23f)) {
        return 0U;
    }
    rounded = open_cfw_bootloader_roundf_427d98(normalized_first);
    if (!(rounded < 0x1.f80002p+5f)) {
        return 0U;
    }
    first_count = (open_cfw_float_ratio_u32)
        open_cfw_bootloader_roundf_427d98(normalized_first);

    if (second_count < 4U) {
        open_cfw_float_ratio_u32 scale = (second_count + 3U) / second_count;
        first_count *= scale;
        second_count *= scale;
    }

    if ((first_count == 0U) || (first_count >= 64U)) {
        return 0U;
    }
    if ((second_count < 4U) || (second_count > 960U)) {
        return 0U;
    }

    *first_ratio = (open_cfw_float_ratio_u8)(first_count & 0x3FU);
    *second_ratio = (open_cfw_float_ratio_u16)(second_count & 0xFFFU);
    return 1U;
}
