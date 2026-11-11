/* Stock BLE bootstrap 0x4df18, peer-manager setup 0x4e4b4 and checked
 * buttonless-DFU setup 0x4c92c. Product event policies remain explicit. */
#include <stdint.h>
#include <stddef.h>
#include "ble.h"
#include "nrf_soc.h"
#include "nrf_ble_gatt.h"
#include "nrf_ble_qwr.h"
#include "peer_manager.h"
#include "ble_dfu.h"
_Static_assert(sizeof(ble_version_t)==6 && offsetof(ble_version_t,company_id)==2 &&
               offsetof(ble_version_t,subversion_number)==4,"native version fields");
_Static_assert(sizeof(ble_gap_sec_params_t)==5,"native peer security parameters");
extern nrf_ble_gatt_t r1_ble_gatt_context;
extern nrf_ble_qwr_t r1_ble_qwr_context_a,r1_ble_qwr_context_b,r1_ble_qwr_context_c;
extern void r1_adc_error(uint32_t);
extern void r1_nordic_gap_identity_configuration(void);
extern void r1_nordic_advertising_configuration(void),r1_bae8_transport_provider_configuration(void);
extern void r1_peer_manager_event_policy(pm_evt_t const *);
extern void r1_buttonless_dfu_event_policy(ble_dfu_buttonless_evt_type_t);
extern uint32_t r1_structured_log_mode_get(void);
extern void r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
volatile ble_version_t r1_ble_controller_version
 __attribute__((section(".r1.ble.controller_version"),aligned(2)))={0};
const char r1_ble_controller_version_ring[]="[RING]ble version: %d, %d, %x";
const char r1_ble_controller_version_sdk[]="ble version: %d, %d, %x";
const char r1_eat_ble_version_ring[]="[RING]ble version: %d, %d, 0x%x";
const char r1_eat_ble_version_sdk[]="ble version: %d, %d, 0x%x";
/* Stock 0x4cbc8: eAT's explicit SoftDevice version diagnostic. */
void r1_eat_ble_version_log(void)
{
    if ((r1_structured_log_mode_get() & 1u) ||
            (r1_structured_log_mode_get() & 4u)) {
        r1_structured_log_format(0x0cc00000u, r1_eat_ble_version_ring,
            r1_eat_ble_version_ring,
            r1_ble_controller_version.version_number,
            r1_ble_controller_version.company_id,
            r1_ble_controller_version.subversion_number);
    }
    if (r1_structured_log_mode_get() & 2u) {
        nrf_log_frontend_std_3(0x001c0003u, r1_eat_ble_version_sdk,
            r1_ble_controller_version.version_number,
            r1_ble_controller_version.company_id,
            r1_ble_controller_version.subversion_number);
    }
}
void r1_dfu_buttonless_init_checked(void)
{
    ble_dfu_buttonless_init_t init={.evt_handler=r1_buttonless_dfu_event_policy};
    uint32_t status=ble_dfu_buttonless_init(&init);
    if (status) r1_adc_error(status);
}
void r1_nordic_peer_manager_configuration(void)
{
    uint32_t status=pm_init();
    if (status) r1_adc_error(status);
    ble_gap_sec_params_t parameters={0};
    parameters.bond=1;
    parameters.io_caps=BLE_GAP_IO_CAPS_NONE;
    parameters.min_key_size=7;
    parameters.max_key_size=16;
    parameters.kdist_own.enc=1;parameters.kdist_own.id=1;
    parameters.kdist_peer.enc=1;parameters.kdist_peer.id=1;
    status=pm_sec_params_set(&parameters);
    if (status) r1_adc_error(status);
    status=pm_register(r1_peer_manager_event_policy);
    if (status) r1_adc_error(status);
}
uint32_t r1_nordic_ble_bootstrap_configuration(void)
{
    r1_nordic_gap_identity_configuration();
    uint32_t status=nrf_ble_gatt_init(&r1_ble_gatt_context,NULL);
    if (status) r1_adc_error(status);
    r1_nordic_advertising_configuration();
    nrf_ble_qwr_init_t qwr={.error_handler=r1_adc_error};
    nrf_ble_qwr_t *contexts[]={&r1_ble_qwr_context_a,&r1_ble_qwr_context_b,&r1_ble_qwr_context_c};
    for (uint32_t i=0;i<3;i++) {
        status=nrf_ble_qwr_init(contexts[i],&qwr);
        if (status) r1_adc_error(status);
    }
    r1_bae8_transport_provider_configuration();
    r1_dfu_buttonless_init_checked();
    r1_nordic_peer_manager_configuration();
    (void)sd_power_dcdc_mode_set(NRF_POWER_DCDC_ENABLE);
    (void)sd_ble_version_get((ble_version_t *)&r1_ble_controller_version);
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
        uint32_t sub=r1_ble_controller_version.subversion_number;
        uint32_t company=r1_ble_controller_version.company_id;
        uint32_t version=r1_ble_controller_version.version_number;
        r1_structured_log_format(0x0cc00000,r1_ble_controller_version_ring,
                                r1_ble_controller_version_ring,version,company,sub);
    }
    if (r1_structured_log_mode_get()&2u) {
        uint32_t sub=r1_ble_controller_version.subversion_number;
        uint32_t company=r1_ble_controller_version.company_id;
        uint32_t version=r1_ble_controller_version.version_number;
        nrf_log_frontend_std_3(0x001c0003,r1_ble_controller_version_sdk,version,company,sub);
    }
    return 0;
}
