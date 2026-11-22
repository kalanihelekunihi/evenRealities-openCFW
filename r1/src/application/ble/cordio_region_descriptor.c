/* Fixed flash ABI used by the source bootloader to initialize the shared
 * lower Cordio RAM without linking against upper-application symbols. */
#if defined(R1_CORDIO_RTC0)
#include <stdint.h>
#include "ble.h"
#include "cordio_dfu_config.h"
#include "cordio_dfu_flash.h"
#include "cordio_dfu_host.h"
#include "../../shared/cordio_region_descriptor.h"

extern uint8_t __r1_cordio_bss_start[];
extern uint8_t __r1_cordio_bss_end[];
extern uint8_t __r1_cordio_data_load[];
extern uint8_t __r1_cordio_data_start[];
extern uint8_t __r1_cordio_data_end[];
extern uint8_t __r1_cordio_code_end[];
extern _Bool r1_cordio_controller_bootstrap(void);
extern void WsfTimerSleepUpdate(void);
extern void wsfOsDispatcher(void);
extern void LlSetBdAddr(const uint8_t *address);
extern void POWER_CLOCK_IRQHandler(void);
extern void RADIO_IRQHandler(void);
extern void TIMER0_IRQHandler(void);
extern void TIMER1_IRQHandler(void);
extern void CCM_AAR_IRQHandler(void);
extern void RTC1_IRQHandler(void);
extern uint32_t sd_ble_gap_device_name_set(ble_gap_conn_sec_mode_t const *permission,
                                            uint8_t const *name, uint16_t length);
extern uint32_t sd_ble_gap_device_name_get(uint8_t *name, uint16_t *length);
extern uint32_t sd_ble_gap_ppcp_set(ble_gap_conn_params_t const *params);
extern uint32_t sd_ble_gap_adv_set_configure(uint8_t *handle,
                                              ble_gap_adv_data_t const *data,
                                              ble_gap_adv_params_t const *params);
extern uint32_t sd_ble_gap_adv_start(uint8_t handle, uint8_t conn_tag);
extern uint32_t sd_ble_gap_adv_stop(uint8_t handle);
extern uint32_t sd_evt_get(uint32_t *event_id);

const r1_cordio_region_descriptor_t r1_cordio_region_descriptor
    __attribute__((section(".r1_cordio_descriptor"), aligned(4), used)) = {
    .magic = R1_CORDIO_DESCRIPTOR_MAGIC,
    .version = R1_CORDIO_DESCRIPTOR_VERSION,
    .bytes = sizeof(r1_cordio_region_descriptor_t),
    .flash_base = R1_CORDIO_FLASH_BASE,
    .flash_limit = R1_CORDIO_FLASH_LIMIT,
    .ram_base = R1_CORDIO_RAM_BASE,
    .ram_limit = R1_CORDIO_RAM_LIMIT,
    .bss_begin = (uint32_t)(uintptr_t)__r1_cordio_bss_start,
    .bss_end = (uint32_t)(uintptr_t)__r1_cordio_bss_end,
    .data_load = (uint32_t)(uintptr_t)__r1_cordio_data_load,
    .data_begin = (uint32_t)(uintptr_t)__r1_cordio_data_start,
    .data_end = (uint32_t)(uintptr_t)__r1_cordio_data_end,
    .code_end = (uint32_t)(uintptr_t)__r1_cordio_code_end,
    .controller_bootstrap = (uint32_t)(uintptr_t)r1_cordio_controller_bootstrap,
    .timer_update = (uint32_t)(uintptr_t)WsfTimerSleepUpdate,
    .dispatch_once = (uint32_t)(uintptr_t)wsfOsDispatcher,
    .ll_set_bd_addr = (uint32_t)(uintptr_t)LlSetBdAddr,
    .clock_irq = (uint32_t)(uintptr_t)POWER_CLOCK_IRQHandler,
    .radio_irq = (uint32_t)(uintptr_t)RADIO_IRQHandler,
    .timer0_irq = (uint32_t)(uintptr_t)TIMER0_IRQHandler,
    .timer1_irq = (uint32_t)(uintptr_t)TIMER1_IRQHandler,
    .ccm_aar_irq = (uint32_t)(uintptr_t)CCM_AAR_IRQHandler,
    .rtc1_irq = (uint32_t)(uintptr_t)RTC1_IRQHandler,
    .dfu_cfg_set = (uint32_t)(uintptr_t)r1_cordio_dfu_cfg_set,
    .dfu_cfg_ready = (uint32_t)(uintptr_t)r1_cordio_dfu_cfg_ready,
    .dfu_manager_enable = (uint32_t)(uintptr_t)r1_cordio_dfu_manager_enable,
    .gap_device_name_set = (uint32_t)(uintptr_t)sd_ble_gap_device_name_set,
    .gap_device_name_get = (uint32_t)(uintptr_t)sd_ble_gap_device_name_get,
    .gap_ppcp_set = (uint32_t)(uintptr_t)sd_ble_gap_ppcp_set,
    .gap_adv_configure = (uint32_t)(uintptr_t)sd_ble_gap_adv_set_configure,
    .gap_adv_start = (uint32_t)(uintptr_t)sd_ble_gap_adv_start,
    .gap_adv_stop = (uint32_t)(uintptr_t)sd_ble_gap_adv_stop,
    .soc_evt_get = (uint32_t)(uintptr_t)sd_evt_get,
    .dfu_flash_register = (uint32_t)(uintptr_t)r1_cordio_dfu_flash_register,
    .dfu_flash_service = (uint32_t)(uintptr_t)r1_cordio_dfu_flash_service,
    .dfu_flash_erase = (uint32_t)(uintptr_t)r1_cordio_dfu_flash_erase,
    .dfu_flash_write = (uint32_t)(uintptr_t)r1_cordio_dfu_flash_write,
    .dfu_host_start = (uint32_t)(uintptr_t)r1_cordio_dfu_host_start,
    .dfu_host_ready = (uint32_t)(uintptr_t)r1_cordio_dfu_host_ready,
    .dfu_host_shutdown = (uint32_t)(uintptr_t)r1_cordio_dfu_host_request_shutdown,
    .dfu_ble_enable = (uint32_t)(uintptr_t)r1_cordio_dfu_ble_enable,
    .dfu_gap_disconnect = (uint32_t)(uintptr_t)r1_cordio_dfu_gap_disconnect,
    .dfu_gap_conn_param_update =
        (uint32_t)(uintptr_t)r1_cordio_dfu_gap_conn_param_update,
    .dfu_gap_data_length_update =
        (uint32_t)(uintptr_t)r1_cordio_dfu_gap_data_length_update,
    .dfu_gap_phy_update = (uint32_t)(uintptr_t)r1_cordio_dfu_gap_phy_update,
    .dfu_gatts_exchange_mtu_reply =
        (uint32_t)(uintptr_t)r1_cordio_dfu_gatts_exchange_mtu_reply,
    .gatts_service_add = (uint32_t)(uintptr_t)sd_ble_gatts_service_add,
    .gatts_characteristic_add =
        (uint32_t)(uintptr_t)sd_ble_gatts_characteristic_add,
    .gatts_hvx = (uint32_t)(uintptr_t)sd_ble_gatts_hvx,
    .gatts_sys_attr_set = (uint32_t)(uintptr_t)sd_ble_gatts_sys_attr_set,
    .gatts_authorize_reply =
        (uint32_t)(uintptr_t)sd_ble_gatts_rw_authorize_reply,
    .dfu_gatts_value_get =
        (uint32_t)(uintptr_t)r1_cordio_dfu_gatts_value_get,
    .dfu_sec_params_reply =
        (uint32_t)(uintptr_t)r1_cordio_dfu_sec_params_reply,
    .dfu_sec_info_reply =
        (uint32_t)(uintptr_t)r1_cordio_dfu_sec_info_reply,
    .dfu_manager_disable =
        (uint32_t)(uintptr_t)r1_cordio_dfu_manager_disable,
};
#endif
