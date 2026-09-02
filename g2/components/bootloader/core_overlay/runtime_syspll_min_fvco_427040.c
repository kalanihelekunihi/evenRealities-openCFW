/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0
 * am_hal_syspll_config_generate_minFVCO(), authenticated at bootloader
 * address 0x00427040.  Names are scoped to openCFW so the leaf can coexist
 * with other HAL revisions in the firmware image.
 */

typedef __UINT8_TYPE__ open_cfw_syspll_u8;
typedef __UINT16_TYPE__ open_cfw_syspll_u16;
typedef __UINT32_TYPE__ open_cfw_syspll_u32;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AAPCS_VFP __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_AAPCS_VFP
#endif

typedef struct open_cfw_syspll_config {
    open_cfw_syspll_u8 reference_select;
    open_cfw_syspll_u8 vco_select;
    open_cfw_syspll_u8 fraction_mode;
    open_cfw_syspll_u8 reference_divider;
    open_cfw_syspll_u8 post_divider_1;
    open_cfw_syspll_u8 post_divider_2;
    open_cfw_syspll_u16 feedback_divider_integer;
    open_cfw_syspll_u32 feedback_divider_fraction;
} open_cfw_syspll_config;

#if defined(OPEN_CFW_SYSPLL_HOST_TEST)
extern const open_cfw_syspll_u8 open_cfw_host_syspll_postdiv_table[50];
#define OPEN_CFW_SYSPLL_POSTDIV_TABLE open_cfw_host_syspll_postdiv_table
#else
#define OPEN_CFW_SYSPLL_POSTDIV_TABLE \
    ((const open_cfw_syspll_u8 *)(__UINTPTR_TYPE__)0x00431e70U)
#endif

extern OPEN_CFW_AAPCS_VFP float
open_cfw_bootloader_float_gcd_426d48(float first, float second);

extern OPEN_CFW_AAPCS_VFP open_cfw_syspll_u32
open_cfw_bootloader_float_encoding_select_426f6c(
    open_cfw_syspll_config *output,
    float reference_mhz,
    float vco_mhz);

__attribute__((used, noinline))
open_cfw_syspll_u32 open_cfw_bootloader_syspll_min_fvco_427040(
    open_cfw_syspll_config *output,
    open_cfw_syspll_u32 reference_hz,
    open_cfw_syspll_u32 output_hz,
    open_cfw_syspll_u32 minimum_vco_hz)
{
    open_cfw_syspll_u32 divider;
    open_cfw_syspll_u32 vco_hz;
    open_cfw_syspll_u32 status;
    open_cfw_syspll_u8 post_divider_1;
    open_cfw_syspll_u8 post_divider_2;
    float output_mhz = (float)output_hz / 1000000.0f;
    float reference_mhz = (float)reference_hz / 1000000.0f;

    if (open_cfw_bootloader_float_gcd_426d48(
            output_mhz, reference_mhz) < 1.0f) {
        open_cfw_syspll_u32 ten_mhz_quotient = reference_hz / 10000000U;
        open_cfw_syspll_u32 pfd_limited_vco = 0U;

        /* Arm UDIV returns zero for a zero divisor when trapping is disabled. */
        if (ten_mhz_quotient != 0U) {
            pfd_limited_vco = reference_hz / ten_mhz_quotient;
        }
        pfd_limited_vco *= 10U;
        if (pfd_limited_vco > minimum_vco_hz) {
            minimum_vco_hz = pfd_limited_vco;
        }
    }

    if (output_hz >= minimum_vco_hz) {
        divider = 1U;
        post_divider_1 = 1U;
        post_divider_2 = 1U;
    } else {
        divider = minimum_vco_hz / output_hz;
        if ((minimum_vco_hz % output_hz) != 0U) {
            divider++;
        }
        if (divider > 49U) {
            return 5U;
        }

        post_divider_1 = OPEN_CFW_SYSPLL_POSTDIV_TABLE[divider];
        post_divider_2 = (open_cfw_syspll_u8)(post_divider_1 & 0x0fU);
        post_divider_1 = (open_cfw_syspll_u8)(post_divider_1 >> 4);
        divider = (open_cfw_syspll_u32)post_divider_1 * post_divider_2;
    }

    vco_hz = output_hz * divider;
    status = open_cfw_bootloader_float_encoding_select_426f6c(
        output,
        reference_mhz,
        (float)vco_hz / 1000000.0f);
    if (status == 0U) {
        open_cfw_syspll_u32 minimum_pfd_hz =
            output->fraction_mode == 0U ? 10000000U : 1000000U;
        open_cfw_syspll_u32 pfd_hz = reference_hz / output->reference_divider;

        if ((reference_hz % output->reference_divider) != 0U) {
            pfd_hz++;
        }
        if (pfd_hz < minimum_pfd_hz) {
            status = 5U;
        } else {
            output->post_divider_1 = post_divider_1;
            output->post_divider_2 = post_divider_2;
        }
    }
    return status;
}
