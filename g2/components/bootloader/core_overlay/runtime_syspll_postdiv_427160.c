/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0
 * am_hal_syspll_config_generate_with_postdiv(), authenticated at bootloader
 * address 0x00427160. Names are scoped to openCFW so this leaf can coexist
 * with other HAL revisions in the firmware image.
 */

typedef __UINT8_TYPE__ open_cfw_syspll_postdiv_u8;
typedef __UINT16_TYPE__ open_cfw_syspll_postdiv_u16;
typedef __UINT32_TYPE__ open_cfw_syspll_postdiv_u32;

typedef struct open_cfw_syspll_postdiv_config {
    open_cfw_syspll_postdiv_u8 reference_select;
    open_cfw_syspll_postdiv_u8 vco_select;
    open_cfw_syspll_postdiv_u8 fraction_mode;
    open_cfw_syspll_postdiv_u8 reference_divider;
    open_cfw_syspll_postdiv_u8 post_divider_1;
    open_cfw_syspll_postdiv_u8 post_divider_2;
    open_cfw_syspll_postdiv_u16 feedback_divider_integer;
    open_cfw_syspll_postdiv_u32 feedback_divider_fraction;
} open_cfw_syspll_postdiv_config;

#if defined(OPEN_CFW_SYSPLL_POSTDIV_HOST_TEST)
extern const open_cfw_syspll_postdiv_u32 open_cfw_host_syspll_pts_a[4];
extern const open_cfw_syspll_postdiv_u32 open_cfw_host_syspll_pts_b[4];
#define OPEN_CFW_SYSPLL_PTS_A open_cfw_host_syspll_pts_a
#define OPEN_CFW_SYSPLL_PTS_B open_cfw_host_syspll_pts_b
#else
#define OPEN_CFW_SYSPLL_PTS_A \
    ((const open_cfw_syspll_postdiv_u32 *)(__UINTPTR_TYPE__)0x00433cb8U)
#define OPEN_CFW_SYSPLL_PTS_B \
    ((const open_cfw_syspll_postdiv_u32 *)(__UINTPTR_TYPE__)0x00433cc8U)
#endif

extern open_cfw_syspll_postdiv_u32
open_cfw_bootloader_syspll_min_fvco_427040(
    open_cfw_syspll_postdiv_config *output,
    open_cfw_syspll_postdiv_u32 reference_hz,
    open_cfw_syspll_postdiv_u32 output_hz,
    open_cfw_syspll_postdiv_u32 minimum_vco_hz);

static __attribute__((always_inline)) inline open_cfw_syspll_postdiv_u32
open_cfw_syspll_points(
    const open_cfw_syspll_postdiv_config *config,
    open_cfw_syspll_postdiv_u32 reference_hz,
    open_cfw_syspll_postdiv_u32 output_hz)
{
    open_cfw_syspll_postdiv_u8 index =
        config->fraction_mode == 0U ? 1U : 0U;
    open_cfw_syspll_postdiv_u32 points;
    open_cfw_syspll_postdiv_u32 output_mhz;

    if (config->vco_select != 0U) {
        index = (open_cfw_syspll_postdiv_u8)(index + 2U);
    }
    points = (reference_hz / 1000000U) * OPEN_CFW_SYSPLL_PTS_B[index];
    points /= config->reference_divider;
    output_mhz = output_hz * config->post_divider_1;
    output_mhz *= config->post_divider_2;
    output_mhz /= 1000000U;
    points += output_mhz * OPEN_CFW_SYSPLL_PTS_A[index];
    return points;
}

__attribute__((used, noinline))
open_cfw_syspll_postdiv_u32 open_cfw_bootloader_syspll_postdiv_427160(
    open_cfw_syspll_postdiv_config *output,
    open_cfw_syspll_postdiv_u32 reference_hz,
    open_cfw_syspll_postdiv_u32 output_hz)
{
    open_cfw_syspll_postdiv_config low_config;
    open_cfw_syspll_postdiv_config high_config;
    const open_cfw_syspll_postdiv_config *selected =
        (const open_cfw_syspll_postdiv_config *)0;
    open_cfw_syspll_postdiv_u8 low_valid;
    open_cfw_syspll_postdiv_u8 high_valid;

    low_valid = (open_cfw_syspll_postdiv_u8)(
        open_cfw_bootloader_syspll_min_fvco_427040(
            &low_config, reference_hz, output_hz, 60000000U) == 0U);
    high_valid = (open_cfw_syspll_postdiv_u8)(
        open_cfw_bootloader_syspll_min_fvco_427040(
            &high_config, reference_hz, output_hz, 240000000U) == 0U);

    if (low_valid != 0U && high_valid != 0U) {
        open_cfw_syspll_postdiv_u32 low_points =
            open_cfw_syspll_points(&low_config, reference_hz, output_hz);
        open_cfw_syspll_postdiv_u32 high_points =
            open_cfw_syspll_points(&high_config, reference_hz, output_hz);
        selected = high_points > low_points ? &low_config : &high_config;
    } else if (high_valid != 0U) {
        selected = &high_config;
    } else if (low_valid != 0U) {
        selected = &low_config;
    }

    if (selected == (const open_cfw_syspll_postdiv_config *)0) {
        return 5U;
    }

    output->vco_select = selected->vco_select;
    output->fraction_mode = selected->fraction_mode;
    output->reference_divider = selected->reference_divider;
    output->post_divider_1 = selected->post_divider_1;
    output->post_divider_2 = selected->post_divider_2;
    output->feedback_divider_integer = selected->feedback_divider_integer;
    output->feedback_divider_fraction = selected->feedback_divider_fraction;
    return 0U;
}
