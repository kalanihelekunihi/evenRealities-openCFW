/* Stock 0x539b8: product BLE resource setup over the pinned SDK/SVC API.
 * The error provider logs and returns; every following setup stage still runs. */
#include <stddef.h>
#include <stdint.h>
#include "ble.h"
#include "nrf_sdh.h"
#include "nrf_sdh_ble.h"
extern void r1_adc_error(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
_Static_assert(sizeof(ble_cfg_t)==12 && sizeof(ble_opt_t)==8,"stock SDK unions");
_Static_assert(offsetof(ble_conn_cfg_t,params)==2,"stock connection config offset");
_Static_assert(BLE_CONN_CFG_GATTS==0x22 && BLE_COMMON_OPT_CONN_EVT_EXT==2,
               "stock configuration and option IDs");
const char r1_softdevice_ram_ring[]="[RING]nrf_sdh_ble ram_start: 0x%x";
const char r1_softdevice_ram_sdk[]="nrf_sdh_ble ram_start: 0x%x";
static void report_error(uint32_t status)
{
 if(status)r1_adc_error(status);
}
void r1_nordic_softdevice_resource_bootstrap_configuration(void)
{
 report_error(nrf_sdh_enable_request());
 uint32_t ram_start=0;
 report_error(nrf_sdh_ble_default_cfg_set(1,&ram_start));
 ble_cfg_t config={0};
 config.conn_cfg.conn_cfg_tag=1;
 config.conn_cfg.params.gatts_conn_cfg.hvn_tx_queue_size=4;
 report_error(sd_ble_cfg_set(BLE_CONN_CFG_GATTS,&config,ram_start));
 if((r1_structured_log_mode_get()&1u) ||
    (r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x0c400000,r1_softdevice_ram_ring,
                               r1_softdevice_ram_ring,ram_start);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1(0x001c0003,r1_softdevice_ram_sdk,ram_start);
 report_error(nrf_sdh_ble_enable(&ram_start));
 ble_opt_t option={0};
 option.common_opt.conn_evt_ext.enable=1;
 report_error(sd_ble_opt_set(BLE_COMMON_OPT_CONN_EVT_EXT,&option));
}
