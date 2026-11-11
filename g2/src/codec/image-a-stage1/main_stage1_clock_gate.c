/* SPDX-License-Identifier: MIT
 * BINH A stage-1 clock-gate dispatcher at stock 0x100005a4.
 * The locked function uses the GRUS module descriptor table and applies
 * the high-gate policy before the all-gate policy. The pinned SDK expresses
 * both policies and keeps the full module domain, including shared gates.
 */
#include <stddef.h>
#include <stdint.h>
#include "clk_priv_stage1.h"
#include <driver/grus_cfg.h>

__attribute__((used, section(".spl_a.clock_gate")))
void gx8002_image_a_stage1_clock_gate_100005a4(uint32_t module,
                                                uint32_t enabled)
{
    _clk_set_high_gate((GX_CLOCK_MODULE)module, enabled);
    (void)_clk_set_all_gate((GX_CLOCK_MODULE)module, enabled);
}

/* Stock 0x100006a4 uses the same module descriptor table as the gate path. */
__attribute__((used, section(".spl_a.clock_frequency")))
uint32_t gx8002_image_a_stage1_clock_frequency_100006a4(uint32_t module)
{
    return (uint32_t)_clk_get_module_frequence((GX_CLOCK_MODULE)module);
}

extern void gx8002_image_a_stage1_osc_32k_state_10000b10(uint32_t);
extern void gx8002_image_a_stage1_osc_all_state_10000b28(uint32_t);
extern uint32_t gx8002_image_a_stage1_flash_read_10000c40(
    uint32_t, void *, uint32_t);

__attribute__((noinline, used, section(".spl_a.clock_div")))
void gx8002_image_a_stage1_clock_div_10000220(uint32_t module,
                                               uint32_t divisor)
{
    _clk_set_div((GX_CLOCK_MODULE)module, divisor);
}

__attribute__((noinline, used, section(".spl_a.clock_dto")))
void gx8002_image_a_stage1_clock_dto_1000034c(uint32_t module,
                                               uint32_t dto, uint32_t enabled)
{
    _clk_set_dto((GX_CLOCK_MODULE)module, dto, enabled);
}

__attribute__((noinline, used, section(".spl_a.clock_source")))
void gx8002_image_a_stage1_clock_source_1000014c(
    GX_CLOCK_SOURCE_TABLE *source)
{
    _clk_set_source(source);
}

__attribute__((noinline, used, section(".spl_a.clock_module")))
int gx8002_image_a_stage1_clock_module_10000414(uint32_t module,
                                                 uint32_t source)
{
    return _clk_set_module((GX_CLOCK_MODULE)module,
                           (GX_CLOCK_MODULE_SOURCE)source);
}

/* The locked initialized table at 0x200011e8 contains ten source/id pairs. */
static GX_CLOCK_SOURCE_TABLE gx_stage1_a_sources[10]
    __attribute__((used, section(".spl_a.clock_sources"))) = {
    {CLOCK_SOURCE_1M_12M, 0}, {CLOCK_SOURCE_32K, 0},
    {CLOCK_SOURCE_24M, 0}, {CLOCK_SOURCE_24M_PLL, 0},
    {CLOCK_SOURCE_32K_PLL, 0}, {CLOCK_SOURCE_1M_INPUT, 0},
    {CLOCK_SOURCE_1M, 0}, {CLOCK_SOURCE_OSC_PLL, 0},
    {CLOCK_SOURCE_PIN_IN, 0}, {CLOCK_SOURCE_PLL_DTO, 0},
};

static GX_CLOCK_SOURCE_TABLE gx_stage1_a_low_sources[2]
    __attribute__((used, section(".spl_a.trim_low_sources"))) = {
    {CLOCK_SOURCE_1M, 0}, {CLOCK_SOURCE_1M_12M, 1},
};
static GX_CLOCK_SOURCE_TABLE gx_stage1_a_high_sources[2]
    __attribute__((used, section(".spl_a.trim_high_sources"))) = {
    {CLOCK_SOURCE_24M, 0}, {CLOCK_SOURCE_24M_PLL, 0},
};

__attribute__((noinline, used, section(".spl_a.clock_trim")))
int gx8002_image_a_stage1_clock_trim_10000860(void)
{
    struct grus_cfg cfg __attribute__((aligned(16)));
    gx8002_image_a_stage1_clock_gate_100005a4(CLOCK_MODULE_OSC_REF, 1u);
    (void)gx8002_image_a_stage1_flash_read_10000c40(
        GRUS_CFG_ADDR, &cfg, sizeof cfg);
    if (cfg.magic != GRUS_CFG_MAGIC)
        return -1;
    const uint8_t *bytes = (const uint8_t *)&cfg;
    uint8_t xor_value = bytes[0];
    for (uint32_t i = 1u; i < sizeof cfg - GRUS_CFG_XOR_LEN; ++i)
        xor_value ^= bytes[i];
    if (xor_value != cfg.xor_result)
        return -1;

    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x24u) =
        cfg.trim_32k_value;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x28u) =
        cfg.trim_1m_value;
    for (uint32_t i = 0u; i < 2u; ++i)
        gx8002_image_a_stage1_clock_source_1000014c(
            &gx_stage1_a_low_sources[i]);
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_OSC + 0x2cu) =
        cfg.trim_24m_value;
    for (uint32_t i = 0u; i < 2u; ++i)
        gx8002_image_a_stage1_clock_source_1000014c(
            &gx_stage1_a_high_sources[i]);
    (void)gx8002_image_a_stage1_clock_module_10000414(
        CLOCK_MODULE_SCPU, MODULE_SOURCE_24M_PLL);
    (void)gx8002_image_a_stage1_clock_module_10000414(
        CLOCK_MODULE_SRAM, MODULE_SOURCE_24M_PLL);
    (void)gx8002_image_a_stage1_clock_module_10000414(
        CLOCK_MODULE_FLASH_SPI, MODULE_SOURCE_24M_PLL);
    gx8002_image_a_stage1_clock_gate_100005a4(CLOCK_MODULE_OSC_REF, 0u);
    return 0;
}

/* Stock 0x10000f34 enables the 32 kHz oscillator only after valid trim. */
__attribute__((noinline, used, section(".spl_a.clock_trim_enable")))
void gx8002_image_a_stage1_clock_trim_enable_10000f34(void)
{
    if (gx8002_image_a_stage1_clock_trim_10000860() == 0)
        gx8002_image_a_stage1_osc_32k_state_10000b10(1u);
}

__attribute__((used, section(".spl_a.clock_init")))
void gx8002_image_a_stage1_clock_init_1000092c(void)
{
    gx8002_image_a_stage1_osc_all_state_10000b28(0u);
    gx8002_image_a_stage1_osc_32k_state_10000b10(0u);
    for (uint32_t module = 0u; module < CLOCK_MODULE_MAX; ++module) {
        gx8002_image_a_stage1_clock_div_10000220(module, 0u);
        gx8002_image_a_stage1_clock_dto_1000034c(module, 0u, 0u);
    }
    for (uint32_t i = 0u; i < 10u; ++i)
        gx8002_image_a_stage1_clock_source_1000014c(&gx_stage1_a_sources[i]);
    for (uint32_t module = 0u; module < CLOCK_MODULE_MAX; ++module)
        (void)gx8002_image_a_stage1_clock_module_10000414(
            module, MODULE_SOURCE_1M_12M);

    gx8002_image_a_stage1_clock_trim_enable_10000f34();
    *(volatile uint32_t *)(uintptr_t)PMU_CFG_SRAM_GATE_ADDR = 1u;
    *(volatile uint32_t *)(uintptr_t)PMU_CFG_CLK_GATE &= ~1u;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_HW_I2C + 0x84u) &= ~1u;
    *(volatile uint32_t *)(uintptr_t)(GX_REG_BASE_HW_I2C + 0xc8u) = 0u;
    for (uint32_t module = 0u; module < CLOCK_MODULE_MAX; ++module) {
        uint32_t enabled = module < 18u &&
                           ((UINT32_C(0x20462) >> module) & 1u) != 0u;
        gx8002_image_a_stage1_clock_gate_100005a4(module, enabled);
    }
}
