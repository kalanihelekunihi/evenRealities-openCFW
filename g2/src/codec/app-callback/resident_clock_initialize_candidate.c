/* SPDX-License-Identifier: MIT
 * Image-A SRAM clock initialization root 0x10025a88. Direct native call
 * order and product tables are retained. Unreduced clock/voltage lowers
 * remain real external imports, not success stubs.
 */
#include <stdint.h>

struct clock_record { uint32_t selector, value; };
extern const struct clock_record gx8002_clock_osc_sources_26904[10];
extern const struct clock_record gx8002_clock_xtal_sources_26954[10];
extern const struct clock_record gx8002_clock_1m_sources_25cd0[2];
extern const struct clock_record gx8002_clock_startmode1_sources_25cf4[2];
extern const int32_t gx8002_clock_startmode_adjustments_25ce0[5];
extern uint32_t gx8002_resident_start_mode_24984(void);
extern uint32_t gx8002_resident_trim_state_24a1c(void);
extern void gx8002_resident_memcpy_25738(void *dst, const void *src,
                                         uint32_t bytes);
extern void gx8002_resident_clock_source_select_24bcc(
    const struct clock_record *record);
extern void gx8002_resident_clock_pll_wait_25060(const uint32_t *config);
extern uint32_t gx8002_resident_clock_pll_wait_timeout_2500c(
    const uint32_t *config, uint32_t limit);
extern uint32_t gx8002_resident_clock_module_source_24be0(
    uint32_t module, uint32_t source);
extern void gx8002_resident_clock_module_divider_24df8(
    uint32_t module, uint32_t divider);
extern void gx8002_resident_clock_module_dto_24f44(
    uint32_t module, uint32_t numerator, uint32_t denominator);
extern void gx8002_resident_platform_gate_25080(uint32_t module,
                                                 uint32_t enabled);
extern uint32_t gx8002_resident_analog_ldo_voltage_246f0(uint32_t voltage);
extern void gx8002_resident_digital_voltage_24730(uint32_t voltage);

/* Runtime aliases below match native loads. The final scatter/copy mechanism
 * must make source-owned initialized records visible at these addresses. */
static volatile uint32_t *const pll_config =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x200268c8);
static volatile uint32_t *const clock_gate_snapshot =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027318);

void gx8002_resident_clock_init_pointer_25a88(
    uint32_t unused0, uint32_t unused1, uint32_t unused2, uint32_t unused3)
{
    (void)unused0; (void)unused1; (void)unused2; (void)unused3;
    (void)gx8002_resident_clock_module_divider_24df8(6u, 1u);
    uint32_t start_mode = gx8002_resident_start_mode_24984();
    if (start_mode == 0u) {
        if (gx8002_resident_trim_state_24a1c() == 1u) {
            pll_config[14] = 1u;
            uint32_t baseline = pll_config[5];
            int32_t adjustment[5];
            gx8002_resident_memcpy_25738(adjustment,
                gx8002_clock_startmode_adjustments_25ce0, 20u);
            uint32_t index = 0u;
            for (;;) {
                pll_config[5] = baseline + (uint32_t)adjustment[index];
                if (gx8002_resident_clock_pll_wait_timeout_2500c(
                        (const uint32_t *)pll_config, 40u) == 0u) break;
                if (++index == 5u) for (;;) { }
            }
            for (uint32_t i = 0; i < 10u; ++i)
                gx8002_resident_clock_source_select_24bcc(
                    &gx8002_clock_osc_sources_26904[i]);
        } else {
            for (uint32_t i = 0; i < 10u; ++i)
                gx8002_resident_clock_source_select_24bcc(
                    &gx8002_clock_xtal_sources_26954[i]);
        }
    } else if (start_mode == 1u) {
        struct clock_record records[2];
        gx8002_resident_memcpy_25738(records,
            gx8002_clock_startmode1_sources_25cf4, 16u);
        if (pll_config[14] == 1u)
            gx8002_resident_clock_pll_wait_25060(
                (const uint32_t *)pll_config);
        gx8002_resident_clock_source_select_24bcc(&records[0]);
        gx8002_resident_clock_source_select_24bcc(&records[1]);
    }

    static const uint8_t source_modules[19] =
        {10,6,0,1,3,4,5,2,7,8,9,22,16,11,19,12,13,14,15};
    static const uint8_t source_values[19] =
        {1,1,2,0,0,0,0,1,3,6,0,0,1,1,1,1,1,1,1};
    for (uint32_t i = 0; i < 19u; ++i)
        (void)gx8002_resident_clock_module_source_24be0(
            source_modules[i], source_values[i]);

    (void)gx8002_resident_clock_module_dto_24f44(2u, UINT32_C(0x1000000), 0u);
    static const uint8_t divider_modules[13] =
        {6,0,1,3,2,7,8,19,10,12,13,15,14};
    static const uint16_t divider_values[13] =
        {1,4,3,2,2,384,12,2,3,1,1,2,2};
    for (uint32_t i = 0; i < 8u; ++i)
        (void)gx8002_resident_clock_module_divider_24df8(
            divider_modules[i], divider_values[i]);
    (void)gx8002_resident_clock_module_dto_24f44(16u, UINT32_C(0x1000000), 0u);
    (void)gx8002_resident_clock_module_dto_24f44(11u, UINT32_C(0x1000000), 1u);
    for (uint32_t i = 8u; i < 13u; ++i)
        (void)gx8002_resident_clock_module_divider_24df8(
            divider_modules[i], divider_values[i]);

    if (start_mode == 1u)
        for (uint32_t module = 11u; module < 26u; ++module)
            gx8002_resident_platform_gate_25080(
                module, (*clock_gate_snapshot >> module) & 1u);
    gx8002_resident_platform_gate_25080(5u, 1u);
    volatile uint32_t *const pll =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005080);
    volatile uint32_t *const analog =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0005000);
    pll[1] &= ~UINT32_C(1);
    analog[0x60u / 4u] &= ~UINT32_C(2);
    analog[0x40u / 4u] = 0x59u;
    analog[0x44u / 4u] = 0x59u;
    analog[0x48u / 4u] = 0x59u;
    analog[0x4cu / 4u] = 0x59u;
    (void)gx8002_resident_analog_ldo_voltage_246f0(0u);
    gx8002_resident_digital_voltage_24730(0u);
}
