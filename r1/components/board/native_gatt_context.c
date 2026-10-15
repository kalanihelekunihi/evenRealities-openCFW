/* Native init writes this 36-byte record; cold startup independently proves
 * its initial zero contents. Role split and live SoftDevice ownership remain
 * separate configuration gates. */
#include "nrf_ble_gatt.h"
nrf_ble_gatt_t r1_ble_gatt_context __attribute__((section(".r1.gatt.context")));
