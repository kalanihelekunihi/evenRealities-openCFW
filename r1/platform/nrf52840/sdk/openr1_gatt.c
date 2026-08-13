#include "openr1_gatt.h"

#include <stdint.h>

#include "ble.h"
#include "nrf_error.h"
#include "nrf_sdh_ble.h"
#include "nrf_ble_gatt.h"

#define OPENR1_ATT_MTU UINT16_C(247)
#define OPENR1_DATA_LENGTH UINT8_C(251)

NRF_BLE_GATT_DEF(gatt);

static uint32_t last_error;

uint32_t openr1_gatt_initialize(void) {
    ret_code_t error = nrf_ble_gatt_init(&gatt, NULL);
    if (error == NRF_SUCCESS) {
        error = nrf_ble_gatt_att_mtu_periph_set(&gatt, OPENR1_ATT_MTU);
    }
    if (error == NRF_SUCCESS) {
        error = nrf_ble_gatt_att_mtu_central_set(&gatt, OPENR1_ATT_MTU);
    }
    if (error == NRF_SUCCESS) {
        error = nrf_ble_gatt_data_length_set(
            &gatt, BLE_CONN_HANDLE_INVALID, OPENR1_DATA_LENGTH);
    }
    last_error = error;
    return error;
}

uint16_t openr1_gatt_effective_mtu(uint16_t connection) {
    return nrf_ble_gatt_eff_mtu_get(&gatt, connection);
}

uint8_t openr1_gatt_effective_data_length(uint16_t connection) {
    uint8_t length = 0u;
    const ret_code_t error = nrf_ble_gatt_data_length_get(
        &gatt, connection, &length);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return 0u;
    }
    return length;
}

uint32_t openr1_gatt_last_error(void) {
    return last_error;
}
