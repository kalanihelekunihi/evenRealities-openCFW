/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room C implementation of the bootloader CLKGEN configuration entry
 * at 0x00426CCC.
 */

typedef __UINT8_TYPE__ open_cfw_clkgen_config_u8;
typedef __UINT32_TYPE__ open_cfw_clkgen_config_u32;

typedef struct {
    open_cfw_clkgen_config_u8 high_speed_enable;
    open_cfw_clkgen_config_u8 clock_select;
    open_cfw_clkgen_config_u8 reserved[2];
    open_cfw_clkgen_config_u32 divider;
} open_cfw_clkgen_config;

typedef union {
    open_cfw_clkgen_config_u32 value;
    struct {
        open_cfw_clkgen_config_u32 clock_select : 2;
        open_cfw_clkgen_config_u32 divider : 29;
        open_cfw_clkgen_config_u32 preserved_top_bit : 1;
    } fields;
} open_cfw_clkgen_divider_register;

#if defined(OPEN_CFW_CLKGEN_CONFIG_HOST_TEST)
extern volatile open_cfw_clkgen_config_u32 open_cfw_clkgen_config_host_control;
extern volatile open_cfw_clkgen_config_u32 open_cfw_clkgen_config_host_mode;
extern volatile open_cfw_clkgen_config_u32 open_cfw_clkgen_config_host_divider;
#define OPEN_CFW_CLKGEN_CONFIG_CONTROL open_cfw_clkgen_config_host_control
#define OPEN_CFW_CLKGEN_CONFIG_MODE open_cfw_clkgen_config_host_mode
#define OPEN_CFW_CLKGEN_CONFIG_DIVIDER open_cfw_clkgen_config_host_divider
#else
#define OPEN_CFW_CLKGEN_CONFIG_CONTROL \
    (*(volatile open_cfw_clkgen_config_u32 *)(__UINTPTR_TYPE__)0x40004020U)
#define OPEN_CFW_CLKGEN_CONFIG_MODE \
    (*(volatile open_cfw_clkgen_config_u32 *)(__UINTPTR_TYPE__)0x4000404CU)
#define OPEN_CFW_CLKGEN_CONFIG_DIVIDER \
    (*(volatile open_cfw_clkgen_config_u32 *)(__UINTPTR_TYPE__)0x40004048U)
#endif

__attribute__((used, noinline))
open_cfw_clkgen_config_u32 open_cfw_bootloader_clkgen_config_426ccc(
    const volatile open_cfw_clkgen_config *configuration)
{
    open_cfw_clkgen_config_u32 value;
    open_cfw_clkgen_divider_register divider_register;

    if (configuration == (const volatile open_cfw_clkgen_config *)0) {
        return 6U;
    }

    OPEN_CFW_CLKGEN_CONFIG_CONTROL |= 7U;

    value = OPEN_CFW_CLKGEN_CONFIG_MODE;
    value &= ~(1U << 29);
    value |= ((open_cfw_clkgen_config_u32)
              (configuration->high_speed_enable & 1U)) << 29;
    OPEN_CFW_CLKGEN_CONFIG_MODE = value;

    divider_register.value = OPEN_CFW_CLKGEN_CONFIG_DIVIDER;
    divider_register.fields.clock_select = configuration->clock_select & 3U;
    OPEN_CFW_CLKGEN_CONFIG_DIVIDER = divider_register.value;

    divider_register.value = OPEN_CFW_CLKGEN_CONFIG_DIVIDER;
    divider_register.fields.divider =
        configuration->divider & 0x1FFFFFFFU;
    OPEN_CFW_CLKGEN_CONFIG_DIVIDER = divider_register.value;

    OPEN_CFW_CLKGEN_CONFIG_MODE |= 1U;
    return 0U;
}
