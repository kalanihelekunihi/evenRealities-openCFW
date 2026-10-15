#include <stdint.h>

/* Native 0x20073b00: three table pointers, a database pointer, one
 * callback pointer, and the active CCC entry count at offset 0x14. */
uint8_t audio_ble_atts_ccc_runtime_20073b00[0x18u];

extern uint32_t audio_ble_atts_ccc_alloc_table_52bb8a(uint32_t);
extern void audio_ble_atts_ccc_update_52bb64(uint32_t, uint32_t,
                                              uint32_t, uint32_t);
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
static const char message[] = "AttsCccInitTable connId=%d";
static const char function_name[] = "AttsCccInitTable";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_ccc.c";

/* Native 0x52c244. */
void audio_ble_slave_apply_record_52c244(uint32_t connection,
                                          const void *initial_values)
{
    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
        audio_ble_hci_vendor_compare_44b610(info_label, error_label, 3u) != 0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(info_label, warn_label, 4u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_ble_hci_vendor_compare_44b610(info_label, info_label, 4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                        audio_ble_hci_vendor_compare_44b610(att_label, hci_label, 3u) != 0)
                        audio_ble_wsf_trace(info_label, message, (uint8_t)connection);
                } else if ((audio_log_flags() & 2u) != 0u) {
                    audio_log_extended(4u, att_label, path, function_name, 0x160u,
                                       message, (uint8_t)connection);
                }
            } else if ((audio_log_flags() & 2u) != 0u) {
                audio_log_extended(3u, att_label, path, function_name, 0x160u,
                                   message, (uint8_t)connection);
            }
        } else if ((audio_log_flags() & 2u) != 0u) {
            audio_log_extended(2u, att_label, path, function_name, 0x160u,
                               message, (uint8_t)connection);
        }
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(1u, att_label, path, function_name, 0x160u,
                           message, (uint8_t)connection);
    }

    uint32_t table = audio_ble_atts_ccc_alloc_table_52bb8a((uint8_t)connection);
    if (table == 0u) return;
    uint8_t count = audio_ble_atts_ccc_runtime_20073b00[0x14u];
    if (initial_values == 0) {
        uint8_t *out = (uint8_t *)(uintptr_t)table;
        for (uint32_t index = 0u; index < (uint32_t)count * 2u; ++index)
            out[index] = 0u;
        return;
    }
    const uint8_t *values = (const uint8_t *)initial_values;
    for (uint32_t route = 0u; route < count; ++route) {
        uint16_t value = (uint16_t)values[route * 2u]
                       | ((uint16_t)values[route * 2u + 1u] << 8u);
        uint8_t *out = (uint8_t *)(uintptr_t)(table + route * 2u);
        out[0] = (uint8_t)value;
        out[1] = (uint8_t)(value >> 8u);
        if (value != 0u)
            audio_ble_atts_ccc_update_52bb64((uint8_t)connection, route, 0u, value);
    }
}
