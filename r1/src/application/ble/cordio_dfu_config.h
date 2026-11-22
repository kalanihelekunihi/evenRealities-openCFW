#ifndef R1_CORDIO_DFU_CONFIG_H
#define R1_CORDIO_DFU_CONFIG_H

#include <stdbool.h>
#include <stdint.h>
#include "ble.h"
#include "nrf_sdm.h"

/* The source bootloader enters this lower-flash C service through the
 * validated region descriptor. Its state is reset by INIT_SD's RAM clear. */
uint32_t r1_cordio_dfu_cfg_set(uint32_t cfg_id, ble_cfg_t const *cfg);
bool r1_cordio_dfu_cfg_ready(void);
uint32_t r1_cordio_dfu_manager_enable(nrf_clock_lf_cfg_t const *clock,
                                      nrf_fault_handler_t fault_handler);
uint32_t r1_cordio_dfu_manager_disable(void);

#endif
