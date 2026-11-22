#ifndef R1_CORDIO_DFU_HOST_H
#define R1_CORDIO_DFU_HOST_H

#include <stdbool.h>
#include <stdint.h>
#include "ble_gap.h"

typedef bool (*r1_cordio_dfu_publish_t)(const void *event, uint16_t length);

bool r1_cordio_dfu_host_start(r1_cordio_dfu_publish_t publish);
uint32_t r1_cordio_dfu_ble_enable(r1_cordio_dfu_publish_t publish,
                                  void *arena, uint32_t arena_bytes,
                                  uint32_t (*uuid_encode)(const ble_uuid_t *,
                                                           uint8_t *, uint8_t *));
bool r1_cordio_dfu_host_ready(void);
bool r1_cordio_dfu_host_idle(void);
void r1_cordio_dfu_host_request_shutdown(void);
uint32_t r1_cordio_dfu_gap_disconnect(uint16_t conn_handle,
                                      uint8_t reason);
uint32_t r1_cordio_dfu_gap_conn_param_update(
    uint16_t conn_handle, const ble_gap_conn_params_t *parameters);
uint32_t r1_cordio_dfu_gap_data_length_update(
    uint16_t conn_handle, const ble_gap_data_length_params_t *parameters,
    ble_gap_data_length_limitation_t *limitation);
uint32_t r1_cordio_dfu_gap_phy_update(uint16_t conn_handle,
                                      const ble_gap_phys_t *phys);
uint32_t r1_cordio_dfu_gatts_exchange_mtu_reply(uint16_t conn_handle,
                                                 uint16_t server_rx_mtu);
uint32_t r1_cordio_dfu_gatts_value_get(uint16_t conn_handle,
                                       uint16_t handle, ble_gatts_value_t *value);
uint32_t r1_cordio_dfu_sec_params_reply(
    uint16_t conn_handle, uint8_t status,
    const ble_gap_sec_params_t *parameters,
    const ble_gap_sec_keyset_t *keys);
uint32_t r1_cordio_dfu_sec_info_reply(
    uint16_t conn_handle, const ble_gap_enc_info_t *enc_info,
    const ble_gap_irk_t *id_info, const ble_gap_sign_info_t *sign_info);

#endif
