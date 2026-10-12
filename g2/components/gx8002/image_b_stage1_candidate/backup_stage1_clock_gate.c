/* SPDX-License-Identifier: MIT
 * Stage1 0x100001f8: source-attributable GX8002 clock-gate dispatcher.
 * Pinned NationalChip arch/soc/grus/spl/spl_clk.c calls the same two static
 * inline policies in arch/soc/grus/include/clk_priv.h. Keep the complete
 * module domain and its descriptor lookup, not a FLASH_SPI-only surrogate.
 */
#include <stdint.h>
#include <stddef.h>
#include <clk_priv.h>
#include <driver/grus_cfg.h>

void gx8002_image_b_stage1_clock_gate_100001f8(
    uint32_t module, uint32_t enabled)
{
    _clk_set_high_gate((GX_CLOCK_MODULE)module, enabled);
    (void)_clk_set_all_gate((GX_CLOCK_MODULE)module, enabled);
}

/* Native 0x10000300 shares the same 26-entry descriptor table and calls the
 * SDK clock-frequency policy. Keep it in this TU so the table has one owner. */
uint32_t gx8002_image_b_stage1_clock_frequency_10000300(uint32_t module)
{
    return (uint32_t)_clk_get_module_frequence((GX_CLOCK_MODULE)module);
}

extern void gx8002_image_b_stage1_osc_32k_state_10000ea0(uint32_t);
extern void gx8002_image_b_stage1_osc_all_state_10000eb8(uint32_t);
extern uint32_t gx8002_image_b_stage1_flash_read_10000fdc(uint32_t, void *, uint32_t);

/* Pinned spl_clk.c:spl_clk_init with the common board's trim transition.
 * The stock data at 0x20001688 has these ten source/id pairs. */
static GX_CLOCK_SOURCE_TABLE gx_stage1_sources[10] = {
    {CLOCK_SOURCE_1M_12M, 0}, {CLOCK_SOURCE_32K, 0},
    {CLOCK_SOURCE_24M, 0}, {CLOCK_SOURCE_24M_PLL, 0},
    {CLOCK_SOURCE_32K_PLL, 0}, {CLOCK_SOURCE_1M_INPUT, 0},
    {CLOCK_SOURCE_1M, 0}, {CLOCK_SOURCE_OSC_PLL, 0},
    {CLOCK_SOURCE_PIN_IN, 0}, {CLOCK_SOURCE_PLL_DTO, 0},
};

static const GX_CLOCK_SOURCE_TABLE gx_stage1_low_sources[2] = {
    {CLOCK_SOURCE_1M, 0}, {CLOCK_SOURCE_1M_12M, 1},
};
static const GX_CLOCK_SOURCE_TABLE gx_stage1_high_sources[2] = {
    {CLOCK_SOURCE_24M, 0}, {CLOCK_SOURCE_24M_PLL, 0},
};

int gx8002_image_b_stage1_clock_trim_100004f4(void)
{
    struct grus_cfg cfg __attribute__((aligned(16)));
    gx8002_image_b_stage1_clock_gate_100001f8(CLOCK_MODULE_OSC_REF, 1);
    (void)gx8002_image_b_stage1_flash_read_10000fdc(GRUS_CFG_ADDR, &cfg, sizeof cfg);
    if (cfg.magic != GRUS_CFG_MAGIC)
        return -1;
    const unsigned char *bytes = (const unsigned char *)&cfg;
    unsigned char x = bytes[0];
    for (uint32_t i = 1; i < sizeof cfg - GRUS_CFG_XOR_LEN; ++i)
        x ^= bytes[i];
    if (x != cfg.xor_result)
        return -1;

    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x24) = cfg.trim_32k_value;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x28) = cfg.trim_1m_value;
    for (uint32_t i = 0; i < 2u; ++i) _clk_set_source((GX_CLOCK_SOURCE_TABLE *)&gx_stage1_low_sources[i]);

    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x2c) = cfg.trim_24m_value;
    for (uint32_t i = 0; i < 2u; ++i) _clk_set_source((GX_CLOCK_SOURCE_TABLE *)&gx_stage1_high_sources[i]);
    (void)_clk_set_module(CLOCK_MODULE_SCPU, MODULE_SOURCE_24M_PLL);
    (void)_clk_set_module(CLOCK_MODULE_SRAM, MODULE_SOURCE_24M_PLL);
    (void)_clk_set_module(CLOCK_MODULE_FLASH_SPI, MODULE_SOURCE_24M_PLL);
    gx8002_image_b_stage1_clock_gate_100001f8(CLOCK_MODULE_OSC_REF, 0);
    return 0;
}

void gx8002_image_b_stage1_clock_init_100007d8(void)
{
    gx8002_image_b_stage1_osc_32k_state_10000ea0(0);
    gx8002_image_b_stage1_osc_all_state_10000eb8(0);
    for (uint32_t i = 0; i < CLOCK_MODULE_MAX; ++i) {
        _clk_set_div((GX_CLOCK_MODULE)i, 0);
        _clk_set_dto((GX_CLOCK_MODULE)i, 0, 0);
    }
    for (uint32_t i = 0; i < 10u; ++i)
        _clk_set_source(&gx_stage1_sources[i]);
    for (uint32_t i = 0; i < CLOCK_MODULE_MAX; ++i)
        (void)_clk_set_module((GX_CLOCK_MODULE)i, MODULE_SOURCE_1M_12M);

    if (gx8002_image_b_stage1_clock_trim_100004f4() == 0)
        gx8002_image_b_stage1_osc_32k_state_10000ea0(1);

    *(volatile uint32_t *)(uintptr_t)PMU_CFG_SRAM_GATE_ADDR = 1;
    *(volatile uint32_t *)(uintptr_t)PMU_CFG_CLK_GATE &= ~1u;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_HW_I2C + 0x84) &= ~1u;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_HW_I2C + 0xc8) = 0;
    for (uint32_t i = CLOCK_MODULE_RTC; i < CLOCK_MODULE_MAX; ++i) {
        uint32_t enable = i == CLOCK_MODULE_PMU || i == CLOCK_MODULE_HW_I2C ||
                          i == CLOCK_MODULE_SRAM || i == CLOCK_MODULE_SCPU ||
                          i == CLOCK_MODULE_UART0;
        gx8002_image_b_stage1_clock_gate_100001f8(i, enable);
    }
}
