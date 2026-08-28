/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>

#include "runtime_mspi_device_configure_provider.h"

typedef struct {
    uint32_t devcfg;
    bool sepio;
    uint32_t xipmixed;
    uint32_t normal_pad;
    uint32_t d4_pad;
} expected_t;

int main(void)
{
    static const expected_t expected[OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT] = {
        { 1, true,  0x000, 0x103, 0x80000013 }, { 2, true,  0x000, 0x103, 0x80000013 },
        { 5, false, 0x000, 0x103, 0x80000013 }, { 6, false, 0x000, 0x103, 0x80000013 },
        { 9, false, 0x000, 0x10F, 0x8000001F }, {10, false, 0x000, 0x10F, 0x8000001F },
        {13, false, 0x000, 0x3FF, 0x000003FF }, {14, false, 0x000, 0x3FF, 0x000003FF },
        {13, false, 0x000, 0x3FF, 0x000003FF }, {14, false, 0x000, 0x3FF, 0x000003FF },
        {17, false, 0x000, 0x7FFFF, 0x0007FFFF }, {18, false, 0x000, 0x7FFFF, 0x0007FFFF },
        { 1, false, 0x100, 0x103, 0x80000013 }, { 2, false, 0x100, 0x103, 0x80000013 },
        { 1, false, 0x300, 0x103, 0x80000013 }, { 2, false, 0x300, 0x103, 0x80000013 },
        { 1, false, 0x500, 0x10F, 0x8000001F }, { 2, false, 0x500, 0x10F, 0x8000001F },
        { 1, false, 0x700, 0x10F, 0x8000001F }, { 2, false, 0x700, 0x10F, 0x8000001F },
        { 1, false, 0x000, 0x103, 0x80000013 }, { 2, false, 0x000, 0x103, 0x80000013 },
        { 1, false, 0x900, 0x3FF, 0x000003FF }, { 2, false, 0x900, 0x3FF, 0x000003FF },
        { 1, false, 0xB00, 0x3FF, 0x000003FF }, { 2, false, 0xB00, 0x3FF, 0x000003FF }
    };
    open_cfw_wave12_mspi_device_plan_t plan;
    uint32_t i;

    assert(OPEN_CFW_WAVE12_MSPI_DEVCFG_MASK == 0x1F);
    assert(OPEN_CFW_WAVE12_MSPI_SEPIO_MASK == 0x02000000);
    assert(OPEN_CFW_WAVE12_MSPI_XIPMIXED_MASK == 0xF00);
    for (i = 0; i < OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT; ++i) {
        assert(open_cfw_wave12_mspi_device_plan(i, false, &plan));
        assert(plan.devcfg_field == expected[i].devcfg);
        assert(plan.separate_input_output == expected[i].sepio);
        assert(plan.xipmixed_field == expected[i].xipmixed);
        assert(plan.padouten == expected[i].normal_pad);
        assert(open_cfw_wave12_mspi_device_plan(i, true, &plan));
        assert(plan.padouten == expected[i].d4_pad);
    }
    assert(!open_cfw_wave12_mspi_device_plan(26, false, &plan));
    assert(!open_cfw_wave12_mspi_device_plan(0, false, 0));
    return 0;
}
