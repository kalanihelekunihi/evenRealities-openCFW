/* Use the pinned Nordic S140 SVCALL gateway rather than a product-owned
 * assembly copy. This C alias exports the SDK body under the existing name;
 * no additional forwarding frame or duplicate gateway is emitted. */
#include "ble_gap.h"
extern __typeof__(sd_ble_gap_addr_get) r1_advertising_controller_address_get
    __attribute__((alias("sd_ble_gap_addr_get")));
