/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bounded floating common-divisor helper
 * at bootloader address 0x00426D48.
 */

typedef __UINT8_TYPE__ open_cfw_float_gcd_u8;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_floorf_427c90(float value);

OPEN_CFW_AAPCS_VFP __attribute__((used, noinline))
float open_cfw_bootloader_float_gcd_426d48(float first, float second)
{
    float large = first;
    float small = second;
    open_cfw_float_gcd_u8 iteration = 0U;

    if (large < small) {
        float temporary = large;
        large = small;
        small = temporary;
    }

    for (;;) {
        float quotient;
        float remainder;

        if (iteration >= 16U) {
            return -1.0f;
        }
        if (small < 0x1p-23f) {
            return large;
        }

        quotient = open_cfw_bootloader_floorf_427c90(large / small);
        remainder = large - quotient * small;
        large = small;
        small = remainder;
        iteration++;
    }
}
