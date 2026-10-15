#include "section_legacy_abi.h"
#include "nrf_sdh_ble.h"
#include "app_error.h"
extern void r1_adc_error(uint32_t);
#undef APP_ERROR_HANDLER
#define APP_ERROR_HANDLER(code) r1_adc_error(code)
_Static_assert(NRF_SDH_BLE_EVT_BUF_SIZE==500,"stock BLE event buffer");
_Static_assert(NRF_SDH_BLE_OBSERVER_PRIO_LEVELS==4,"stock observer ranges");
_Static_assert(sizeof(nrf_sdh_ble_evt_observer_t)==8,"stock observer pair");
