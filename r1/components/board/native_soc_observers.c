/* Native first priority-0 record; storage supplies the second record. */
#include "nrf_sdh_soc.h"
extern void r1_soc_observer_907fc(uint32_t,void *);
extern void ble_dfu_buttonless_on_sys_evt(uint32_t,void *);
const nrf_sdh_soc_evt_observer_t r1_soc_observer_priority0
 __attribute__((section(".r1.soc.observer0"),aligned(4)))={r1_soc_observer_907fc,0};
const nrf_sdh_soc_evt_observer_t r1_soc_observer_priority1
 __attribute__((section(".sdh_soc_observers1"),aligned(4)))={ble_dfu_buttonless_on_sys_evt,0};
