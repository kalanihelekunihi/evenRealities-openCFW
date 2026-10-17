/* Cordio attsCsfActClientState; stock Main 0x52caa8. */
#include <stdint.h>
extern uint8_t audio_ble_connection_state_table[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);
static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "ATT";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c";
static const char function[] = "attsCsfActClientState";
static const char change_message[] = "ConnId %d change aware state is %d";
static const char sync_message[] = "ConnId %d out of sync, PDU with opcode 0x%02x ignored!";
static void trace_info(uint32_t line, const char *message, uint32_t connection,
                       uint32_t value)
{
    uint8_t level;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(info_tag, error_tag, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(info_tag, warning_tag, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(info_tag, info_tag, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0)
            audio_ble_hci_wsf_trace(info_tag, message, connection, value);
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, line,
                           message, connection, value);
}
uint8_t audio_ble_atts_csf_act_client_state_52caa8(uint16_t handle,
                                                      uint8_t opcode,
                                                      const uint8_t *packet)
{
    if (opcode == 2u || opcode == 0x1eu)
        return 0u;
    uint8_t *const row = audio_ble_connection_state_table + (uint32_t)handle * 2u;
    uint8_t error = 0u;
    if (row[1u] == 3u) {
        if ((opcode & 0x40u) == 0u) {
            row[1u] = 1u;
            trace_info(0xb3u, change_message, (uint32_t)handle + 1u, 1u);
        }
        if ((opcode & 0x40u) != 0u || (row[0u] & 1u) != 0u)
            error = 0x12u;
    } else if (row[1u] == 1u) {
        if ((opcode & 0x40u) == 0u) {
            row[1u] = 0u;
            trace_info(0xc8u, change_message, (uint32_t)handle + 1u, 0u);
            void (*callback)(uint8_t, uint8_t, uint8_t *) =
                *(void (**)(uint8_t, uint8_t, uint8_t *))
                (audio_ble_connection_state_table + 8u);
            if (callback != 0)
                callback((uint8_t)(handle + 1u), row[1u], row);
        } else {
            error = 0x12u;
        }
    }
    if (opcode == 8u && packet[13u] == 0x2au && packet[14u] == 0x2bu) {
        error = 0u;
        if (audio_ble_connection_state_table[12u] != 0u) {
            row[1u] = 2u;
            trace_info(0xefu, change_message, (uint32_t)handle + 1u, 2u);
        }
    }
    if (error == 0x12u)
        trace_info(0xf6u, sync_message, (uint32_t)handle + 1u, opcode);
    return error;
}
