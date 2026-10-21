#ifndef R1_APPLICATION_SDK_CANDIDATE_CONFIG_H
#define R1_APPLICATION_SDK_CANDIDATE_CONFIG_H
/* Historical seed: preserve the original file and its confidence distinctions. */
#include "../../../config-recovered/sdk_config.h"
/* Stock nrfx_gpiote_init: 16 handler slots, pin assignments +64,
 * configured pins +120, state +126. With 8 hardware channels this is
 * eight low-power slots, not the historical seed's two. */
#undef NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS
#define NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS 8
/* Stock NVIC IPR byte at IRQ6 is 0xC0: priority 6 with three priority bits. */
#undef NRFX_GPIOTE_CONFIG_IRQ_PRIORITY
#define NRFX_GPIOTE_CONFIG_IRQ_PRIORITY 6
/* Body-level source evidence in NORDIC-SDK-CORRELATION.md. */
#undef SEGGER_RTT_CONFIG_BUFFER_SIZE_DOWN
#define SEGGER_RTT_CONFIG_BUFFER_SIZE_DOWN 64
#undef NRF_LOG_ENABLED
#define NRF_LOG_ENABLED 1
#define NRF_LOG_DEFERRED 1
#define NRF_BLE_QWR_ENABLED 1
#define NRF_BLE_QWR_MAX_ATTR 0
#define BLE_DFU_ENABLED 1
#define NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS 0
#define NRF_PWR_MGMT_ENABLED 1
#define NRF_PWR_MGMT_CONFIG_USE_SCHEDULER 0
#define NRF_BALLOC_ENABLED 1
#define NRF_MEMOBJ_ENABLED 1
#define NRF_RINGBUF_ENABLED 1
#define NRF_FPRINTF_ENABLED 1
#define NRF_LOG_BACKEND_RTT_ENABLED 1
/* Remaining missing values are declared SDK example defaults, NOT stock facts.
 * The build generates this unmodified header from the authenticated archive. */
#include "r1_sdk_example_defaults.h"
/* The SDK example declares disabled legacy drivers; apply_old_config.h would
 * overwrite the recovered nrfx values with those defaults. Remove only these
 * legacy namespaces; nrf_drv_twi/nrf_drv_clock keep their required aliases. */
#undef GPIOTE_ENABLED
#undef RTC_ENABLED
#undef RTC0_ENABLED
#undef RTC1_ENABLED
#undef RTC2_ENABLED
#undef RTC_DEFAULT_CONFIG_FREQUENCY
#undef RTC_DEFAULT_CONFIG_RELIABLE
#undef RTC_DEFAULT_CONFIG_IRQ_PRIORITY
#undef RTC_CONFIG_LOG_ENABLED
#undef RTC_CONFIG_LOG_LEVEL
#undef RTC_CONFIG_INFO_COLOR
#undef RTC_CONFIG_DEBUG_COLOR
#undef SAADC_ENABLED
#undef SAADC_CONFIG_RESOLUTION
#undef SAADC_CONFIG_OVERSAMPLE
#undef SAADC_CONFIG_LP_MODE
#undef SAADC_CONFIG_IRQ_PRIORITY
#undef SAADC_CONFIG_LOG_ENABLED
#undef SAADC_CONFIG_LOG_LEVEL
#undef SAADC_CONFIG_INFO_COLOR
#undef SAADC_CONFIG_DEBUG_COLOR
#undef SPI_ENABLED
#undef WDT_ENABLED
#undef WDT_CONFIG_BEHAVIOUR
#undef WDT_CONFIG_RELOAD_VALUE
#undef WDT_CONFIG_IRQ_PRIORITY
#undef WDT_CONFIG_NO_IRQ
#undef WDT_CONFIG_LOG_ENABLED
#undef WDT_CONFIG_LOG_LEVEL
#undef WDT_CONFIG_INFO_COLOR
#undef WDT_CONFIG_DEBUG_COLOR
#undef PDM_ENABLED
/* Stock NFCT/PDM IRQ bodies prove the modules are linked. Configuration fields
 * not separately recovered remain example candidates, not hardware facts. */
/* IRQ body evidence selects TIMER2 and TIMER4 (first/second control blocks),
 * NORDIC-SDK-CORRELATION.md:684-685. TIMER4 also backs the NFCT workaround. */
#undef TIMER_ENABLED
#undef TIMER0_ENABLED
#undef TIMER1_ENABLED
#undef TIMER2_ENABLED
#undef TIMER3_ENABLED
#undef TIMER4_ENABLED
#undef NRFX_TIMER_ENABLED
#undef NRFX_TIMER0_ENABLED
#undef NRFX_TIMER1_ENABLED
#undef NRFX_TIMER2_ENABLED
#undef NRFX_TIMER3_ENABLED
#undef NRFX_TIMER4_ENABLED
#define NRFX_TIMER_ENABLED 1
#define NRFX_TIMER0_ENABLED 0
#define NRFX_TIMER1_ENABLED 0
#define NRFX_TIMER2_ENABLED 1
#define NRFX_TIMER3_ENABLED 0
#define NRFX_TIMER4_ENABLED 1
#undef NRFX_NFCT_ENABLED
#define NRFX_NFCT_ENABLED 1
#undef NRFX_PDM_ENABLED
#define NRFX_PDM_ENABLED 1
#endif
