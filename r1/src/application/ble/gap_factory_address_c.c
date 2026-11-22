/* Source-built GAP identity before privacy or user address configuration.
 * The Cordio R1 PAL loads the same FICR address into the controller.
 */
#include "ble_gap.h"
#include "nrf_error.h"
#include "r1_factory_ble_address.h"
#if defined(SVCALL_AS_NORMAL_FUNCTION) && !defined(FREERTOS)
#include "../../bootloader/runtime/cordio_region_init.h"
#endif

#if defined(SVCALL_AS_NORMAL_FUNCTION)
static ble_gap_addr_t selected_address;
static uint8_t selected_address_valid;

uint32_t sd_ble_gap_addr_get(ble_gap_addr_t *address)
{
    if (address == 0) return NRF_ERROR_INVALID_ADDR;
    if (selected_address_valid) {
        *address = selected_address;
        return NRF_SUCCESS;
    }
    address->addr_id_peer = 0;
    address->addr_type = BLE_GAP_ADDR_TYPE_RANDOM_STATIC;
    r1_factory_ble_address_load(address->addr);
    return NRF_SUCCESS;
}

#if !defined(FREERTOS)
uint32_t sd_ble_gap_addr_set(ble_gap_addr_t const *address)
{
    if (address == 0) return NRF_ERROR_INVALID_ADDR;
    if (address->addr_id_peer != 0u ||
        address->addr_type != BLE_GAP_ADDR_TYPE_RANDOM_STATIC ||
        (address->addr[5] & 0xc0u) != 0xc0u) {
        return NRF_ERROR_INVALID_PARAM;
    }
    uint8_t all_zero = 1u;
    uint8_t all_one = 1u;
    for (unsigned i = 0; i < 5u; ++i) {
        all_zero &= address->addr[i] == 0u;
        all_one &= address->addr[i] == 0xffu;
    }
    all_zero &= (address->addr[5] & 0x3fu) == 0u;
    all_one &= (address->addr[5] & 0x3fu) == 0x3fu;
    if (all_zero || all_one) return NRF_ERROR_INVALID_PARAM;
    if (!r1_bootloader_cordio_set_bd_addr(address->addr))
        return NRF_ERROR_INVALID_STATE;
    selected_address = *address;
    selected_address_valid = 1u;
    return NRF_SUCCESS;
}
#endif
#endif
