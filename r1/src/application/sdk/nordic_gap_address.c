/* Use the pinned Nordic S140 SVCALL gateway in the stock-compatible build.
 * A source-built SoftDevice port declares SVCALL as a normal function, so
 * its gateway has no local body to alias; forward through the C ABI then. */
#include "ble_gap.h"
#if defined(SVCALL_AS_NORMAL_FUNCTION)
uint32_t r1_advertising_controller_address_get(ble_gap_addr_t *address)
{
    return sd_ble_gap_addr_get(address);
}
#else
extern __typeof__(sd_ble_gap_addr_get) r1_advertising_controller_address_get
    __attribute__((alias("sd_ble_gap_addr_get")));
#endif
