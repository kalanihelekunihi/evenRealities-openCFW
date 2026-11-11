#ifndef R1_NATIVE_HW_TWI_LEGACY_TX_H
#define R1_NATIVE_HW_TWI_LEGACY_TX_H
#include "nrf_drv_twi.h"

/* Stock has two copies of the SDK legacy-instance transmit wrapper. */
ret_code_t r1_twi_primary_legacy_tx(const nrf_drv_twi_t *,uint8_t,const uint8_t *,uint8_t,bool);
ret_code_t r1_twi_secondary_legacy_tx(const nrf_drv_twi_t *,uint8_t,const uint8_t *,uint8_t,bool);
#endif
