/* SPDX-License-Identifier: MIT */
#include <stdint.h>

uint32_t open_cfw_hwinit_host_registers[4][0x40 / 4];
uint32_t open_cfw_hwinit_host_chip_revision;
uint32_t open_cfw_hwinit_host_global_control;
uint32_t open_cfw_hwinit_host_mode_count;
uint32_t open_cfw_hwinit_host_mode_value;
uint32_t open_cfw_hwinit_host_route_value;
uint32_t open_cfw_hwinit_host_clock_count;
uint32_t open_cfw_hwinit_host_clock_index;
uint32_t open_cfw_hwinit_host_clock_requested;
uint32_t open_cfw_hwinit_host_clock_actual;
uint32_t open_cfw_hwinit_host_clock_status;

void open_cfw_hwinit_host_mode_route(uint32_t mode, uint32_t route)
{
    open_cfw_hwinit_host_mode_count++;
    open_cfw_hwinit_host_mode_value = mode;
    open_cfw_hwinit_host_route_value = route;
}

uint32_t open_cfw_hwinit_host_clock_divider(uint32_t index, uint32_t requested, uint32_t *actual)
{
    open_cfw_hwinit_host_clock_count++;
    open_cfw_hwinit_host_clock_index = index;
    open_cfw_hwinit_host_clock_requested = requested;
    if (open_cfw_hwinit_host_clock_status == 0U) *actual = open_cfw_hwinit_host_clock_actual;
    return open_cfw_hwinit_host_clock_status;
}

#include "../../components/bootloader/core_overlay/runtime_hw_initializer_42308e.c"
