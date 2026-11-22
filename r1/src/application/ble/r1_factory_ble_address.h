/* Factory BLE identity shared by the R1 Nordic API and Cordio controller.
 * nRF52840 FICR.DEVICEADDR is a 48-bit, little-endian factory address.
 * The source-built R1 stack uses it as a random static identity.
 */
#ifndef R1_FACTORY_BLE_ADDRESS_H
#define R1_FACTORY_BLE_ADDRESS_H

#include <stdint.h>
#include "nrf.h"

static inline void r1_factory_ble_address_load(uint8_t address[6])
{
    uint32_t low = NRF_FICR->DEVICEADDR[0];
    uint32_t high = NRF_FICR->DEVICEADDR[1];
    address[0] = (uint8_t)low;
    address[1] = (uint8_t)(low >> 8);
    address[2] = (uint8_t)(low >> 16);
    address[3] = (uint8_t)(low >> 24);
    address[4] = (uint8_t)high;
    address[5] = (uint8_t)(high >> 8) | UINT8_C(0xc0);
}

#endif
