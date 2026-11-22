#ifndef R1_CORDIO_BLE_EVENT_BRIDGE_H
#define R1_CORDIO_BLE_EVENT_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>

/* Cordio DM uses connection IDs 1..3. The Nordic application indexes 0..2. */
bool r1_cordio_gap_connected(uint8_t conn_id, uint16_t hci_handle,
                            uint8_t role, uint8_t addr_type,
                            const uint8_t peer_addr[6], uint16_t interval,
                            uint16_t latency, uint16_t timeout);
bool r1_cordio_gap_disconnected(uint8_t conn_id, uint16_t hci_handle,
                               uint8_t reason);
bool r1_cordio_gap_conn_updated(uint8_t conn_id, uint16_t hci_handle,
                               uint16_t interval, uint16_t latency,
                               uint16_t timeout);
bool r1_cordio_gap_data_length_updated(uint8_t conn_id, uint16_t hci_handle,
                                      uint16_t tx_octets, uint16_t tx_time,
                                      uint16_t rx_octets, uint16_t rx_time);
bool r1_cordio_gap_phy_updated(uint8_t conn_id, uint16_t hci_handle,
                              uint8_t status, uint8_t tx_phy,
                              uint8_t rx_phy);
uint8_t r1_cordio_conn_id_from_nordic(uint16_t nordic_handle);
uint16_t r1_cordio_hci_handle_from_nordic(uint16_t nordic_handle);
void r1_cordio_dm_disconnect(uint8_t conn_id, uint8_t reason);
void r1_cordio_dm_set_data_length(uint8_t conn_id, uint16_t tx_octets,
                                  uint16_t tx_time);
void r1_cordio_dm_conn_param_update(uint8_t conn_id, uint16_t min_interval,
                                    uint16_t max_interval, uint16_t latency,
                                    uint16_t timeout);
void r1_cordio_dm_set_phy(uint8_t conn_id, uint8_t all_phys,
                          uint8_t tx_phys, uint8_t rx_phys);
void r1_cordio_adv_started(uint8_t status);
void r1_cordio_adv_stopped(uint8_t status);
void r1_cordio_adv_event_overflow(void);
void r1_cordio_dm_adv_config(uint8_t type, uint8_t peer_type,
                             const uint8_t peer_addr[6], uint16_t interval,
                             uint8_t channels, const uint8_t *adv_data,
                             uint8_t adv_length, const uint8_t *scan_data,
                             uint8_t scan_length);
void r1_cordio_dm_adv_start(uint16_t duration_ms);
void r1_cordio_dm_adv_stop(void);
void r1_cordio_att_mtu_request(uint8_t conn_id, uint16_t mtu);
bool r1_cordio_att_mtu_updated(uint8_t conn_id, uint16_t mtu);
void r1_cordio_att_read_request(uint8_t conn_id, uint16_t handle,
                                uint16_t offset);
void r1_cordio_att_read_by_type_request(uint8_t conn_id, uint16_t first,
                                        uint16_t last, uint16_t uuid);
bool r1_cordio_att_read_response(uint8_t conn_id, uint8_t kind,
                                 uint8_t status, uint16_t handle,
                                 const uint8_t *data, uint16_t length);
bool r1_cordio_gatts_ccc_changed(uint8_t conn_id, uint16_t handle,
                                 uint16_t value);
bool r1_cordio_gatts_write_event(uint8_t conn_id, uint16_t handle,
                                 uint8_t uuid_type, uint16_t uuid,
                                 uint8_t opcode, const uint8_t *data,
                                 uint16_t length, bool authorize);
bool r1_cordio_gatts_tx_event(uint8_t conn_id, uint16_t handle,
                              bool indication, bool service_changed);
bool r1_cordio_ble_event_publish(const void *event, uint16_t length);
void r1_cordio_ll_set_adv_tx_power(int8_t power);
uint8_t r1_cordio_ll_set_conn_tx_power(uint16_t hci_handle, int8_t power);

#endif
