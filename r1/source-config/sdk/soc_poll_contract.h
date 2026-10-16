#include "section_legacy_abi.h"
#include "nrf_sdh_soc.h"
#include "app_error.h"
extern void r1_adc_error(uint32_t);
#undef APP_ERROR_HANDLER
#define APP_ERROR_HANDLER(code) r1_adc_error(code)
_Static_assert(NRF_SDH_SOC_OBSERVER_PRIO_LEVELS==2,"native SOC ranges");
_Static_assert(sizeof(nrf_sdh_soc_evt_observer_t)==8,"native SOC record");
