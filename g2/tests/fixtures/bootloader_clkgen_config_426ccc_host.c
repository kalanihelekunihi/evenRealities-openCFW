/* SPDX-License-Identifier: MIT */

#include <assert.h>
#include <stdint.h>

volatile uint32_t open_cfw_clkgen_config_host_control;
volatile uint32_t open_cfw_clkgen_config_host_mode;
volatile uint32_t open_cfw_clkgen_config_host_divider;

typedef struct {
    uint8_t high_speed_enable;
    uint8_t clock_select;
    uint8_t reserved[2];
    uint32_t divider;
} test_configuration;

uint32_t open_cfw_bootloader_clkgen_config_426ccc(
    const volatile test_configuration *configuration);

static void verify(
    test_configuration configuration,
    uint32_t initial_control,
    uint32_t initial_mode,
    uint32_t initial_divider,
    uint32_t expected_control,
    uint32_t expected_mode,
    uint32_t expected_divider)
{
    open_cfw_clkgen_config_host_control = initial_control;
    open_cfw_clkgen_config_host_mode = initial_mode;
    open_cfw_clkgen_config_host_divider = initial_divider;
    assert(open_cfw_bootloader_clkgen_config_426ccc(&configuration) == 0U);
    assert(open_cfw_clkgen_config_host_control == expected_control);
    assert(open_cfw_clkgen_config_host_mode == expected_mode);
    assert(open_cfw_clkgen_config_host_divider == expected_divider);
}

int main(void)
{
    test_configuration configuration = {1U, 2U, {0U, 0U}, 0x01234567U};
    assert(open_cfw_bootloader_clkgen_config_426ccc(0) == 6U);

    verify(configuration, 0x80000000U, 0x40000000U, 0x80000001U,
           0x80000007U, 0x60000001U, 0x848D159EU);

    configuration.high_speed_enable = 2U;
    configuration.clock_select = 7U;
    configuration.divider = 0xFFFFFFFFU;
    verify(configuration, 0xFFFFFFF8U, 0xFFFFFFFFU, 0U,
           0xFFFFFFFFU, 0xDFFFFFFFU, 0x7FFFFFFFU);
    return 0;
}
