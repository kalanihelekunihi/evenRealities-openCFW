/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room reconstruction of the authenticated G2 bootloader pin-group
 * dispatcher. Fixed SRAM and pin-controller seams are isolated for tests.
 */

typedef __UINT8_TYPE__ open_cfw_pin_u8;
typedef __UINT32_TYPE__ open_cfw_pin_u32;
typedef __UINTPTR_TYPE__ open_cfw_pin_uintptr;

enum {
    OPEN_CFW_PIN_CONFIG_BASE = 0x20000000U,
    OPEN_CFW_PIN_CONFIGURE_THUMB = 0x0041D92DU
};

typedef open_cfw_pin_u32 (*open_cfw_pin_configure_fn)(
    open_cfw_pin_u32,
    open_cfw_pin_u32);

#if defined(OPEN_CFW_PIN_GROUPS_HOST)
open_cfw_pin_u32 open_cfw_pin_groups_host_config(open_cfw_pin_u32 offset);
open_cfw_pin_u32 open_cfw_pin_groups_host_configure(
    open_cfw_pin_u32 pin,
    open_cfw_pin_u32 configuration);
#endif

static __attribute__((always_inline)) inline open_cfw_pin_u32
open_cfw_pin_group_configuration(open_cfw_pin_u32 offset)
{
#if defined(OPEN_CFW_PIN_GROUPS_HOST)
    return open_cfw_pin_groups_host_config(offset);
#else
    return *(const volatile open_cfw_pin_u32 *)(open_cfw_pin_uintptr)
        (OPEN_CFW_PIN_CONFIG_BASE + offset);
#endif
}

static __attribute__((always_inline)) inline void open_cfw_pin_group_apply(
    open_cfw_pin_u32 pin,
    open_cfw_pin_u32 offset)
{
    const open_cfw_pin_u32 configuration =
        open_cfw_pin_group_configuration(offset);
#if defined(OPEN_CFW_PIN_GROUPS_HOST)
    (void)open_cfw_pin_groups_host_configure(pin, configuration);
#else
    (void)((open_cfw_pin_configure_fn)(open_cfw_pin_uintptr)
        OPEN_CFW_PIN_CONFIGURE_THUMB)(pin, configuration);
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_zero_common(void)
{
    open_cfw_pin_group_apply(0xC7U, 0x00U);
    open_cfw_pin_group_apply(0x40U, 0x04U);
    open_cfw_pin_group_apply(0x41U, 0x08U);
    open_cfw_pin_group_apply(0x48U, 0x24U);
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_zero_pair(void)
{
    open_cfw_pin_group_apply(0x42U, 0x0CU);
    open_cfw_pin_group_apply(0x43U, 0x10U);
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_zero_quad(void)
{
    open_cfw_pin_u32 index;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_pin_group_apply(0x44U + index, 0x14U + index * 4U);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_zero_nine(void)
{
    open_cfw_pin_u32 index;
    for (index = 0U; index < 9U; ++index) {
        open_cfw_pin_group_apply(0x25U + index, 0x28U + index * 4U);
    }
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_one_common(void)
{
    open_cfw_pin_group_apply(0x31U, 0x4CU);
    open_cfw_pin_group_apply(0x5FU, 0x50U);
    open_cfw_pin_group_apply(0x60U, 0x54U);
    open_cfw_pin_group_apply(0x67U, 0x70U);
    open_cfw_pin_group_apply(0x68U, 0x74U);
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_one_pair(void)
{
    open_cfw_pin_group_apply(0x61U, 0x58U);
    open_cfw_pin_group_apply(0x62U, 0x5CU);
}

static __attribute__((always_inline)) inline void
open_cfw_pin_group_bank_one_quad(void)
{
    open_cfw_pin_u32 index;
    for (index = 0U; index < 4U; ++index) {
        open_cfw_pin_group_apply(0x63U + index, 0x60U + index * 4U);
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_pin_groups_41fadc(
    open_cfw_pin_u32 bank,
    open_cfw_pin_u32 subtype_value)
{
    const open_cfw_pin_u8 subtype = (open_cfw_pin_u8)subtype_value;

    if (bank == 0U) {
        if (subtype == 10U) {
            open_cfw_pin_group_bank_zero_nine();
        }
        if (subtype == 10U || subtype == 6U || subtype == 8U) {
            open_cfw_pin_group_bank_zero_quad();
        }
        if (subtype == 10U || subtype == 6U || subtype == 8U ||
            subtype == 4U || subtype == 16U || subtype == 18U) {
            open_cfw_pin_group_bank_zero_pair();
        }
        if (subtype == 0U || subtype == 4U || subtype == 6U ||
            subtype == 8U || subtype == 10U || subtype == 16U ||
            subtype == 18U) {
            open_cfw_pin_group_bank_zero_common();
        }
        return;
    }

    if (bank == 1U) {
        if (subtype == 6U || subtype == 8U || subtype == 22U ||
            subtype == 24U) {
            open_cfw_pin_group_bank_one_quad();
        }
        if (subtype == 4U || subtype == 6U || subtype == 8U ||
            subtype == 16U || subtype == 18U || subtype == 22U ||
            subtype == 24U) {
            open_cfw_pin_group_bank_one_pair();
        }
        if (subtype == 0U || subtype == 4U || subtype == 6U ||
            subtype == 8U || subtype == 16U || subtype == 18U ||
            subtype == 22U || subtype == 24U) {
            open_cfw_pin_group_bank_one_common();
        }
    }
}
