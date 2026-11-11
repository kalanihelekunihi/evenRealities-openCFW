/* Native 0x78a24/0x78a32: instantiate the pinned Nordic SDK legacy TX path.
 * The unit disables sibling calls to retain the native provider call frame.
 * The fifth argument uses its declared C parameter. */
#include "native_hw_twi_legacy_tx.h"
_Static_assert(sizeof(nrf_drv_twi_t)==16 && offsetof(nrf_drv_twi_t,u)==4,"native embedded TWIM instance");

__attribute__((noinline)) ret_code_t r1_twi_primary_legacy_tx(
        const nrf_drv_twi_t *instance,uint8_t address,const uint8_t *data,uint8_t length,bool no_stop)
{
    return nrf_drv_twi_tx(instance,address,data,length,no_stop);
}

__attribute__((noinline)) ret_code_t r1_twi_secondary_legacy_tx(
        const nrf_drv_twi_t *instance,uint8_t address,const uint8_t *data,uint8_t length,bool no_stop)
{
    return nrf_drv_twi_tx(instance,address,data,length,no_stop);
}
