#include "nrf_sdh_ble.h"
/* Typed records from the authenticated four native priority ranges.
 * Unimplemented handlers and opaque context objects stay real dependencies. */
extern void nrf_ble_gatt_on_ble_evt(ble_evt_t const *,void *);
extern void ble_advertising_on_ble_evt(ble_evt_t const *,void *);
extern void r1_connection_parameter_ble_observer(ble_evt_t const *,void *);
extern void r1_sdk_peer_manager_event(ble_evt_t const *,void *);
extern void nrf_ble_qwr_on_ble_evt(ble_evt_t const *,void *);
extern void r1_bae8_raw_observer(ble_evt_t const *,void *);
extern void ble_dfu_buttonless_on_ble_evt(ble_evt_t const *,void *);
extern void r1_gap_event_plan_build(ble_evt_t const *,void *);
extern unsigned char r1_ble_gatt_context[],r1_ble_advertising_context_a[],r1_ble_advertising_context_b[];
extern unsigned char r1_ble_qwr_context_a[],r1_ble_qwr_context_b[],r1_ble_qwr_context_c[];
extern unsigned char r1_native_bae8_service[],r1_ble_dfu_context[];
const nrf_sdh_ble_evt_observer_t r1_ble_observers_priority1[]
 __attribute__((section(".sdh_ble_observers1"),aligned(4)))={
    {nrf_ble_gatt_on_ble_evt,r1_ble_gatt_context},
    {ble_advertising_on_ble_evt,r1_ble_advertising_context_a},
    {r1_connection_parameter_ble_observer,0},
    {ble_advertising_on_ble_evt,r1_ble_advertising_context_b},
    {r1_sdk_peer_manager_event,0}
};
const nrf_sdh_ble_evt_observer_t r1_ble_observers_priority2[]
 __attribute__((section(".sdh_ble_observers2"),aligned(4)))={
    {nrf_ble_qwr_on_ble_evt,r1_ble_qwr_context_a},
    {nrf_ble_qwr_on_ble_evt,r1_ble_qwr_context_b},
    {nrf_ble_qwr_on_ble_evt,r1_ble_qwr_context_c},
    {r1_bae8_raw_observer,r1_native_bae8_service},
    {ble_dfu_buttonless_on_ble_evt,r1_ble_dfu_context}
};
const nrf_sdh_ble_evt_observer_t r1_ble_observers_priority3[]
 __attribute__((section(".sdh_ble_observers3"),aligned(4)))={{r1_gap_event_plan_build,0}};
_Static_assert(sizeof(r1_ble_observers_priority1)==40,"stock priority 1 bytes");
_Static_assert(sizeof(r1_ble_observers_priority2)==40,"stock priority 2 bytes");
_Static_assert(sizeof(r1_ble_observers_priority3)==8,"stock priority 3 bytes");
