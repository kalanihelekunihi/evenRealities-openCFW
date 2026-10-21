#include <stdint.h>

extern uint8_t audio_ble_connection_state_table[];
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_ble_wsf_trace(const char *, ...);

static const char error_label[] = "ERR";
static const char warn_label[] = "WARN";
static const char info_label[] = "INFO";
static const char att_label[] = "ATT";
static const char hci_label[] = "HCI";
static const char invalid[] = "Invalid connId in AttsCsfConnOpen: %d";
static const char function_name[] = "AttsCsfConnOpen";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_csf.c";

/* Native 0x52d370. The first CSF row starts at RAM 0x20073e04. */
void audio_ble_slave_apply_flags_52d370(uint32_t connection, uint32_t flag,
                                         uint32_t features)
{
    connection = (uint8_t)connection;
    if (connection != 0u) {
        uint8_t *row = (uint8_t *)(uintptr_t)
            ((uintptr_t)audio_ble_connection_state_table + (connection - 1u) * 2u);
        if (features == 0u) {
            row[0] = 0u;
            row[1] = 0u;
        } else {
            row[1] = (uint8_t)flag;
            (void)audio_queue_copy_bytes(row, (const void *)(uintptr_t)features, 1u);
        }
        return;
    }
    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
        audio_ble_hci_vendor_compare_44b610(warn_label, error_label, 3u) != 0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(warn_label, warn_label, 4u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_ble_hci_vendor_compare_44b610(warn_label, info_label, 4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                        audio_ble_hci_vendor_compare_44b610(att_label, hci_label, 3u) != 0)
                        audio_ble_wsf_trace(warn_label, invalid, connection);
                } else if ((audio_log_flags() & 2u) != 0u) {
                    audio_log_extended(4u, att_label, path, function_name, 0x137u,
                                       invalid, connection);
                }
            } else if ((audio_log_flags() & 2u) != 0u) {
                audio_log_extended(3u, att_label, path, function_name, 0x137u,
                                   invalid, connection);
            }
        } else if ((audio_log_flags() & 2u) != 0u) {
            audio_log_extended(2u, att_label, path, function_name, 0x137u,
                               invalid, connection);
        }
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(1u, att_label, path, function_name, 0x137u,
                           invalid, connection);
    }
}
