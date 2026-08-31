/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_device_configure_424120.h"

enum { OPEN_CFW_DEVICE_MAX_WRITES = 3 };

typedef struct open_cfw_device_fixture {
    open_cfw_mspi_dev_u32 devcfg;
    open_cfw_mspi_dev_u32 devxip;
    open_cfw_mspi_dev_u32 read_count;
    open_cfw_mspi_dev_u32 write_count;
    open_cfw_mspi_dev_u32 addresses[OPEN_CFW_DEVICE_MAX_WRITES];
    open_cfw_mspi_dev_u32 values[OPEN_CFW_DEVICE_MAX_WRITES];
} open_cfw_device_fixture;

static open_cfw_device_fixture fixture;

static open_cfw_mspi_dev_u32 read_reg(void *context,
                                      open_cfw_mspi_dev_u32 address)
{
    open_cfw_device_fixture *state = context;
    state->read_count++;
    if ((address & 0xfffU) == 0x84U) return state->devcfg;
    if ((address & 0xfffU) == 0x90U) return state->devxip;
    return 0U;
}

static void write_reg(void *context, open_cfw_mspi_dev_u32 address,
                      open_cfw_mspi_dev_u32 value)
{
    open_cfw_device_fixture *state = context;
    if (state->write_count < OPEN_CFW_DEVICE_MAX_WRITES) {
        state->addresses[state->write_count] = address;
        state->values[state->write_count] = value;
    }
    if ((address & 0xfffU) == 0x84U) state->devcfg = value;
    if ((address & 0xfffU) == 0x90U) state->devxip = value;
    state->write_count++;
}

void open_cfw_test_mspi_device_reset(open_cfw_mspi_dev_u32 devcfg,
                                     open_cfw_mspi_dev_u32 devxip)
{
    open_cfw_mspi_dev_u32 index;
    fixture.devcfg = devcfg;
    fixture.devxip = devxip;
    fixture.read_count = 0U;
    fixture.write_count = 0U;
    for (index = 0U; index < OPEN_CFW_DEVICE_MAX_WRITES; index++) {
        fixture.addresses[index] = 0U;
        fixture.values[index] = 0U;
    }
}

open_cfw_mspi_dev_u32 open_cfw_test_mspi_device_run(
    open_cfw_mspi_dev_u32 module, open_cfw_mspi_dev_u32 clock_on_d4,
    open_cfw_mspi_dev_u32 device_configuration)
{
    const open_cfw_mspi_device_state instance = {
        0U, module, 0U, (open_cfw_mspi_dev_u8)clock_on_d4,
        (open_cfw_mspi_dev_u8)device_configuration
    };
    const open_cfw_mspi_device_ports ports = {
        &fixture, read_reg, write_reg
    };
    return open_cfw_bootloader_mspi_device_configure_424120(&instance, &ports);
}

open_cfw_mspi_dev_u32 open_cfw_test_mspi_device_value(
    open_cfw_mspi_dev_u32 selector, open_cfw_mspi_dev_u32 index)
{
    if (selector == 0U) return fixture.read_count;
    if (selector == 1U) return fixture.write_count;
    if (selector == 2U) return fixture.devcfg;
    if (selector == 3U) return fixture.devxip;
    if (selector == 4U && index < OPEN_CFW_DEVICE_MAX_WRITES)
        return fixture.addresses[index];
    if (selector == 5U && index < OPEN_CFW_DEVICE_MAX_WRITES)
        return fixture.values[index];
    return 0U;
}

#include "../../components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c"
