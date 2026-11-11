/* Compile the pinned SDK implementation once. Its private SVCI object must
 * also serve the recovered backend; a second zeroed object would split state.
 * The compiler alias exports that same allocation without an accessor call.
 * See r1/docs/reference/dfu-state-owner-review.md. */
#include <stddef.h>
#include "ble_dfu_unbonded.c"
_Static_assert(sizeof(nrf_dfu_set_adv_name_svci_async_t)==12 &&
 offsetof(nrf_dfu_set_adv_name_svci_async_t,async_func)==0 &&
 offsetof(nrf_dfu_set_adv_name_svci_async_t,sys_evt_handler)==4 &&
 offsetof(nrf_dfu_set_adv_name_svci_async_t,state)==8,
 "stock asynchronous DFU state layout");
extern __typeof__(nrf_dfu_set_adv_name_svci_async_def) r1_dfu_svci_async_state
 __attribute__((alias("nrf_dfu_set_adv_name_svci_async_def")));
