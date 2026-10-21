/* Cordio HCI connection command payloads at Apollo Main 0x52b0be..0x52b743. */
#include <stdint.h>

extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

static void put16(uint8_t *p, uint16_t value)
{
    p[0] = (uint8_t)value;
    p[1] = (uint8_t)(value >> 8u);
}

void audio_ble_hci_remote_conn_param_req_reply_52b0be(
    uint16_t handle, uint16_t min_interval, uint16_t max_interval,
    uint16_t latency, uint16_t timeout, uint16_t min_ce, uint16_t max_ce)
{
    uint8_t *cmd = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x2020u, 14u);
    if (cmd == 0) return;
    put16(cmd + 3u, handle);
    put16(cmd + 5u, min_interval);
    put16(cmd + 7u, max_interval);
    put16(cmd + 9u, latency);
    put16(cmd + 11u, timeout);
    put16(cmd + 13u, min_ce);
    put16(cmd + 15u, max_ce);
    audio_ble_hci_cmd_send(cmd);
}

void audio_ble_hci_remote_conn_param_req_neg_reply_52b146(
    uint16_t handle, uint8_t reason)
{
    uint8_t *cmd = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x2021u, 3u);
    if (cmd == 0) return;
    put16(cmd + 3u, handle);
    cmd[5u] = reason;
    audio_ble_hci_cmd_send(cmd);
}

void audio_ble_hci_set_data_len_52b176(
    uint16_t handle, uint16_t octets, uint16_t time)
{
    uint8_t *cmd = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x2022u, 6u);
    if (cmd == 0) return;
    put16(cmd + 3u, handle);
    put16(cmd + 5u, octets);
    put16(cmd + 7u, time);
    audio_ble_hci_cmd_send(cmd);
}

void audio_ble_hci_write_auth_payload_timeout_52b70c(
    uint16_t handle, uint16_t timeout)
{
    uint8_t *cmd = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x0c7cu, 4u);
    if (cmd == 0) return;
    put16(cmd + 3u, handle);
    put16(cmd + 5u, timeout);
    audio_ble_hci_cmd_send(cmd);
}
