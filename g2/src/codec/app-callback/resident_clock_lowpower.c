/* SPDX-License-Identifier: MIT
 * Image-A SRAM low-power clock helpers at 0x1002599c and 0x10025a00.
 * Direct native branches and loop bound, with real selected clock lowers.
 */
#include <stdint.h>

extern uint32_t gx8002_resident_clock_module_query_24d70(uint32_t module);
extern uint32_t gx8002_resident_clock_module_source_24be0(
    uint32_t module, uint32_t source);
extern void gx8002_resident_clock_module_divider_24df8(
    uint32_t module, uint32_t divider);
extern uint32_t gx8002_resident_clock_gate_query_25180(uint32_t module);
extern void gx8002_resident_clock_pll_wait_25060(const uint32_t *config);
extern void gx8002_resident_memcpy_25738(void *dst, const void *src,
                                         uint32_t bytes);
struct gx8002_clock_record { uint32_t selector, value; };
extern const struct gx8002_clock_record gx8002_clock_1m_sources_25cd0[2];
extern void gx8002_resident_clock_source_select_24bcc(
    const struct gx8002_clock_record *record);

/* Stock 0x1002599C (gx8002_clock_lowpower_init_shared) */
void gx8002_resident_clock_lowpower_init_2599c(void)
{
    volatile uint32_t *const status =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa001008c);
    for (uint32_t module = 0u; module < 26u; ++module) {
        if (module == 7u) {
            if (gx8002_resident_clock_module_query_24d70(module) != 3u)
                continue;
            (void)gx8002_resident_clock_module_source_24be0(module, 4u);
        } else if (module == 8u) {
            if (gx8002_resident_clock_module_query_24d70(module) != 5u)
                continue;
            (void)gx8002_resident_clock_module_source_24be0(module, 6u);
        } else if (module == 2u) {
            if (gx8002_resident_clock_module_query_24d70(module) == 1u &&
                (*status & UINT32_C(0x40)) != 0u)
                continue;
            (void)gx8002_resident_clock_module_source_24be0(2u, 0u);
        } else {
            (void)gx8002_resident_clock_module_source_24be0(module, 0u);
        }
    }
}

/* Stock 0x10025A00 (gx8002_audio_lowpower_divider) */
void gx8002_resident_clock_pair_dividers_zero_25a00(void)
{
    gx8002_resident_clock_module_divider_24df8(7u, 0u);
    gx8002_resident_clock_module_divider_24df8(8u, 0u);
}

/* Stock 0x10025A14 (gx8002_clock_switch_1m) */
void gx8002_resident_clock_switch_1m_25a14(void)
{
    struct gx8002_clock_record records[2];
    gx8002_resident_memcpy_25738(records,
        gx8002_clock_1m_sources_25cd0, 16u);
    gx8002_resident_clock_source_select_24bcc(&records[0]);
    gx8002_resident_clock_source_select_24bcc(&records[1]);
    gx8002_resident_clock_lowpower_init_2599c();

    volatile uint32_t *const snapshot =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20027318);
    for (uint32_t module = 11u; module < 26u; ++module) {
        uint32_t gate = gx8002_resident_clock_gate_query_25180(module);
        if (gate != UINT32_MAX)
            *snapshot = *snapshot | ((gate & 1u) << module);
    }
    gx8002_resident_clock_pair_dividers_zero_25a00();
    gx8002_resident_clock_module_divider_24df8(10u, 0u);
    volatile uint32_t *const pll =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x200268c8);
    if (*pll == 1u) {
        *pll = 0u;
        gx8002_resident_clock_pll_wait_25060((const uint32_t *)pll);
        *pll = 1u;
    }
}
