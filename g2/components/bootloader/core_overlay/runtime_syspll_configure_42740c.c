/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Reviewable C realization of AmbiqSuite 5.1.0 am_hal_syspll_configure(),
 * authenticated at bootloader address 0x0042740C.
 */

typedef __UINT8_TYPE__ open_cfw_syspll_configure_u8;
typedef __UINT16_TYPE__ open_cfw_syspll_configure_u16;
typedef __UINT32_TYPE__ open_cfw_syspll_configure_u32;

typedef struct open_cfw_syspll_configure_state {
    open_cfw_syspll_configure_u32 prefix;
    open_cfw_syspll_configure_u32 module;
} open_cfw_syspll_configure_state;

typedef struct open_cfw_syspll_configure_config {
    open_cfw_syspll_configure_u8 fref;
    open_cfw_syspll_configure_u8 vco_select;
    open_cfw_syspll_configure_u8 fraction_mode;
    open_cfw_syspll_configure_u8 reference_divider;
    open_cfw_syspll_configure_u8 post_divider_1;
    open_cfw_syspll_configure_u8 post_divider_2;
    open_cfw_syspll_configure_u16 feedback_divider_integer;
    open_cfw_syspll_configure_u32 feedback_divider_fraction;
} open_cfw_syspll_configure_config;

#define OPEN_CFW_SYSPLL_CONFIGURE_HANDLE_MASK 0x01ffffffU
#define OPEN_CFW_SYSPLL_CONFIGURE_HANDLE_MAGIC 0x01504c30U
#define OPEN_CFW_SYSPLL_CONFIGURE_ENABLE_BIT 0x02000000U
#define OPEN_CFW_SYSPLL_CONFIGURE_INVALID_HANDLE 2U
#define OPEN_CFW_SYSPLL_CONFIGURE_INVALID_ARGUMENT 6U
#define OPEN_CFW_SYSPLL_CONFIGURE_INVALID_OPERATION 7U

#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_VCOSELECT (1U << 9)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FREFSEL (1U << 5)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_DACPD (1U << 4)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_DSMPD (1U << 3)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUT4PHASEPD (1U << 2)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUTPOSTDIVPD (1U << 1)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUTVCOPD (1U << 0)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_FRAC_MASK 0x00ffffffU
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_FBDIV_MASK (0x0fffU << 16)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_REFDIV_MASK 0x0000003fU
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_POSTDIV1_MASK (7U << 12)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_POSTDIV2_MASK (7U << 8)

#if defined(OPEN_CFW_SYSPLL_CONFIGURE_HOST_TEST)
extern open_cfw_syspll_configure_u32
open_cfw_host_syspll_configure_pllctl0_read(void);
extern void open_cfw_host_syspll_configure_pllctl0_write(
    open_cfw_syspll_configure_u32 value);
extern open_cfw_syspll_configure_u32
open_cfw_host_syspll_configure_plldiv0_read(void);
extern void open_cfw_host_syspll_configure_plldiv0_write(
    open_cfw_syspll_configure_u32 value);
extern open_cfw_syspll_configure_u32
open_cfw_host_syspll_configure_plldiv1_read(void);
extern void open_cfw_host_syspll_configure_plldiv1_write(
    open_cfw_syspll_configure_u32 value);
extern void open_cfw_host_syspll_configure_fref_update(
    open_cfw_syspll_configure_u32 fref);
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ() \
    open_cfw_host_syspll_configure_pllctl0_read()
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(value) \
    open_cfw_host_syspll_configure_pllctl0_write(value)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_READ() \
    open_cfw_host_syspll_configure_plldiv0_read()
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_WRITE(value) \
    open_cfw_host_syspll_configure_plldiv0_write(value)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ() \
    open_cfw_host_syspll_configure_plldiv1_read()
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(value) \
    open_cfw_host_syspll_configure_plldiv1_write(value)
#define OPEN_CFW_SYSPLL_CONFIGURE_FREF_UPDATE(value) \
    open_cfw_host_syspll_configure_fref_update(value)
#else
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0 \
    (*(volatile open_cfw_syspll_configure_u32 *)0x400204d8U)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0 \
    (*(volatile open_cfw_syspll_configure_u32 *)0x400204dcU)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1 \
    (*(volatile open_cfw_syspll_configure_u32 *)0x400204e0U)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ() \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(value) \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0 = (value))
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_READ() \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_WRITE(value) \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0 = (value))
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ() \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1)
#define OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(value) \
    (OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1 = (value))
extern void open_cfw_bootloader_sysctrl_pll_fref_update_41ac92(
    open_cfw_syspll_configure_u32 fref);
#define OPEN_CFW_SYSPLL_CONFIGURE_FREF_UPDATE(value) \
    open_cfw_bootloader_sysctrl_pll_fref_update_41ac92(value)
#endif

static open_cfw_syspll_configure_u32
open_cfw_syspll_configure_replace(open_cfw_syspll_configure_u32 value,
                                  open_cfw_syspll_configure_u32 mask,
                                  open_cfw_syspll_configure_u32 field)
{
    return (value & ~mask) | (field & mask);
}

__attribute__((used, noinline))
open_cfw_syspll_configure_u32 open_cfw_bootloader_row6_configure_42740c(
    open_cfw_syspll_configure_state *state,
    const open_cfw_syspll_configure_config *config)
{
    open_cfw_syspll_configure_u32 value;
    open_cfw_syspll_configure_u16 feedback;

    if (state == (open_cfw_syspll_configure_state *)0 ||
            (state->prefix & OPEN_CFW_SYSPLL_CONFIGURE_HANDLE_MASK) !=
                OPEN_CFW_SYSPLL_CONFIGURE_HANDLE_MAGIC) {
        return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_HANDLE;
    }
    if ((state->prefix & OPEN_CFW_SYSPLL_CONFIGURE_ENABLE_BIT) != 0U) {
        return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_OPERATION;
    }
    if (config->reference_divider > 63U) {
        return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_ARGUMENT;
    }

    feedback = config->feedback_divider_integer;
    if (config->fraction_mode == 1U) {
        if (feedback < 4U || feedback > 960U) {
            return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_ARGUMENT;
        }
    } else if (feedback < 10U || feedback > 96U) {
        return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_ARGUMENT;
    }

    if (config->post_divider_1 > 7U ||
            config->post_divider_2 > 7U ||
            config->post_divider_2 > config->post_divider_1) {
        return OPEN_CFW_SYSPLL_CONFIGURE_INVALID_ARGUMENT;
    }

    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_VCOSELECT,
        ((open_cfw_syspll_configure_u32)config->vco_select & 1U) << 9));
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FREFSEL,
        ((open_cfw_syspll_configure_u32)config->fref & 1U) << 5));
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_DSMPD,
        ((open_cfw_syspll_configure_u32)config->fraction_mode & 1U) << 3));

    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV0_FRAC_MASK,
        config->feedback_divider_fraction));

    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_FBDIV_MASK,
        (open_cfw_syspll_configure_u32)feedback << 16));
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_REFDIV_MASK,
        config->reference_divider));
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_POSTDIV1_MASK,
        (open_cfw_syspll_configure_u32)config->post_divider_1 << 12));
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_WRITE(open_cfw_syspll_configure_replace(
        value, OPEN_CFW_SYSPLL_CONFIGURE_PLLDIV1_POSTDIV2_MASK,
        (open_cfw_syspll_configure_u32)config->post_divider_2 << 8));

    OPEN_CFW_SYSPLL_CONFIGURE_FREF_UPDATE(config->fref);

    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(
        value & ~OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_DACPD);
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(
        value | OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUTVCOPD);
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(
        value & ~OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUTPOSTDIVPD);
    value = OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_READ();
    OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_WRITE(
        value & ~OPEN_CFW_SYSPLL_CONFIGURE_PLLCTL0_FOUT4PHASEPD);

    return 0U;
}
