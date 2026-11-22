#ifndef R1_BOOTLOADER_CORDIO_REGION_INIT_H
#define R1_BOOTLOADER_CORDIO_REGION_INIT_H

#include <stdbool.h>
#include <stdint.h>
#include "ble.h"
#include "nrf_sdm.h"

/* INIT_SD must succeed before either lower-flash entry point is called.
 * Controller bootstrap does not install a DFU host or run WSF dispatch. */
uint32_t r1_bootloader_cordio_region_init(void);
bool r1_bootloader_cordio_controller_bootstrap(void);
bool r1_bootloader_cordio_dispatch_once(void);
bool r1_bootloader_cordio_dfu_host_start(void);
bool r1_bootloader_cordio_dfu_host_ready(void);
uint32_t r1_bootloader_cordio_dfu_ble_enable(void *arena,
                                             uint32_t arena_bytes);
bool r1_bootloader_cordio_set_bd_addr(const uint8_t address[6]);
uint32_t r1_bootloader_cordio_dfu_cfg_set(uint32_t cfg_id,
                                            ble_cfg_t const *cfg);
bool r1_bootloader_cordio_dfu_cfg_ready(void);
uint32_t r1_bootloader_cordio_dfu_manager_enable(
    nrf_clock_lf_cfg_t const *clock, nrf_fault_handler_t fault_handler);

#endif
