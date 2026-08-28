/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Software-only provider model derived from the authenticated AmbiqSuite
 * Apollo510 mspi_device_configure implementation.  It performs no MMIO.
 */
#include "runtime_mspi_device_configure_provider.h"

typedef struct {
    uint8_t devcfg;
    uint8_t sepio;
    uint16_t xipmixed;
    uint32_t normal_padouten;
} device_row_t;

enum {
    PAD_SERIAL = 0x00000103U,
    PAD_QUAD = 0x0000010FU,
    PAD_OCTAL = 0x000003FFU,
    PAD_HEX = 0x0007FFFFU,
    PAD_D4_SERIAL = 0x80000013U,
    PAD_D4_QUAD = 0x8000001FU
};

static const device_row_t k_device_rows[OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT] = {
    { 1, 1, 0x000, PAD_SERIAL }, { 2, 1, 0x000, PAD_SERIAL },
    { 5, 0, 0x000, PAD_SERIAL }, { 6, 0, 0x000, PAD_SERIAL },
    { 9, 0, 0x000, PAD_QUAD },   {10, 0, 0x000, PAD_QUAD },
    {13, 0, 0x000, PAD_OCTAL },  {14, 0, 0x000, PAD_OCTAL },
    {13, 0, 0x000, PAD_OCTAL },  {14, 0, 0x000, PAD_OCTAL },
    {17, 0, 0x000, PAD_HEX },    {18, 0, 0x000, PAD_HEX },
    { 1, 0, 0x100, PAD_SERIAL }, { 2, 0, 0x100, PAD_SERIAL },
    { 1, 0, 0x300, PAD_SERIAL }, { 2, 0, 0x300, PAD_SERIAL },
    { 1, 0, 0x500, PAD_QUAD },   { 2, 0, 0x500, PAD_QUAD },
    { 1, 0, 0x700, PAD_QUAD },   { 2, 0, 0x700, PAD_QUAD },
    { 1, 0, 0x000, PAD_SERIAL }, { 2, 0, 0x000, PAD_SERIAL },
    { 1, 0, 0x900, PAD_OCTAL },  { 2, 0, 0x900, PAD_OCTAL },
    { 1, 0, 0xB00, PAD_OCTAL },  { 2, 0, 0xB00, PAD_OCTAL }
};

bool
open_cfw_wave12_mspi_device_plan(
    uint32_t device,
    bool clock_on_d4,
    open_cfw_wave12_mspi_device_plan_t *plan)
{
    const device_row_t *row;

    if (plan == 0 || device >= OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT) {
        return false;
    }
    row = &k_device_rows[device];
    plan->devcfg_field = row->devcfg;
    plan->separate_input_output = row->sepio != 0;
    plan->xipmixed_field = row->xipmixed;
    plan->padouten = row->normal_padouten;
    if (clock_on_d4 && row->normal_padouten == PAD_SERIAL) {
        plan->padouten = PAD_D4_SERIAL;
    } else if (clock_on_d4 && row->normal_padouten == PAD_QUAD) {
        plan->padouten = PAD_D4_QUAD;
    }
    return true;
}
