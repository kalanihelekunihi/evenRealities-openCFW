/* Authenticated native stack/state records; unresolved callbacks stay providers. */
#include "nrf_sdh.h"
extern void r1_sdk_ble_events_poll(void *);
extern void r1_sdk_soc_events_poll(void *);
extern void r1_sdh_state_observer_567ac(nrf_sdh_state_evt_t,void *);
extern void r1_sdh_state_observer_890f0(nrf_sdh_state_evt_t,void *);
const nrf_sdh_stack_observer_t r1_sdh_stack_observers[]
 __attribute__((section(".r1.sdh.stack.records"),aligned(4)))={
 {r1_sdk_ble_events_poll,0},{r1_sdk_soc_events_poll,0}
};
const nrf_sdh_state_observer_t r1_sdh_native_state_observers[]
 __attribute__((section(".r1.sdh.state.records"),aligned(4)))={
 {r1_sdh_state_observer_567ac,0},{r1_sdh_state_observer_890f0,0}
};
_Static_assert(sizeof(nrf_sdh_stack_observer_t)==8,"native stack record");
_Static_assert(sizeof(nrf_sdh_state_observer_t)==8,"native state record");
