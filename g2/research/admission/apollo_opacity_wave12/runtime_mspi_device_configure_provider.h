/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Software-only provider model derived from the authenticated AmbiqSuite
 * Apollo510 mspi_device_configure implementation.  It performs no MMIO.
 */
#ifndef OPEN_CFW_WAVE12_MSPI_DEVICE_CONFIGURE_PROVIDER_H
#define OPEN_CFW_WAVE12_MSPI_DEVICE_CONFIGURE_PROVIDER_H

#include <stdbool.h>
#include <stdint.h>

enum {
    OPEN_CFW_WAVE12_MSPI_DEVICE_COUNT = 26,
    OPEN_CFW_WAVE12_MSPI_DEVCFG_MASK = 0x0000001FU,
    OPEN_CFW_WAVE12_MSPI_SEPIO_MASK = 0x02000000U,
    OPEN_CFW_WAVE12_MSPI_XIPMIXED_MASK = 0x00000F00U
};

typedef struct {
    uint32_t devcfg_field;
    bool separate_input_output;
    uint32_t xipmixed_field;
    uint32_t padouten;
} open_cfw_wave12_mspi_device_plan_t;

bool open_cfw_wave12_mspi_device_plan(
    uint32_t device,
    bool clock_on_d4,
    open_cfw_wave12_mspi_device_plan_t *plan);

#endif
