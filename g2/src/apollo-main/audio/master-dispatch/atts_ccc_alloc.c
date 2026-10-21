#include <stdint.h>

extern uint8_t audio_ble_atts_ccc_runtime_20073b00[];
extern void *audio_wsf_buffer_alloc(uint16_t);
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
static const char invalid[] = "Invalid connId in attsCccAllocTbl: %d";
static const char function_name[] = "attsCccAllocTbl";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_ccc.c";

/* Native 0x52bb8a. */
uint32_t audio_ble_atts_ccc_alloc_table_52bb8a(uint32_t connection)
{
    connection = (uint8_t)connection;
    if (connection == 0u) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(warn_label, error_label, 3u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_ble_hci_vendor_compare_44b610(warn_label, warn_label, 4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                    audio_ble_hci_vendor_compare_44b610(warn_label, info_label, 4u) != 0) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                            audio_ble_hci_vendor_compare_44b610(att_label, hci_label, 3u) != 0)
                            audio_ble_wsf_trace(warn_label, invalid, 0u);
                    } else if ((audio_log_flags() & 2u) != 0u) {
                        audio_log_extended(4u, att_label, path, function_name, 0x67u,
                                           invalid, 0u);
                    }
                } else if ((audio_log_flags() & 2u) != 0u) {
                    audio_log_extended(3u, att_label, path, function_name, 0x67u,
                                       invalid, 0u);
                }
            } else if ((audio_log_flags() & 2u) != 0u) {
                audio_log_extended(2u, att_label, path, function_name, 0x67u,
                                   invalid, 0u);
            }
        } else if ((audio_log_flags() & 2u) != 0u) {
            audio_log_extended(1u, att_label, path, function_name, 0x67u,
                               invalid, 0u);
        }
        return 0u;
    }
    uint32_t *slot = (uint32_t *)(void *)
        (audio_ble_atts_ccc_runtime_20073b00 + (connection - 1u) * 4u);
    if (*slot == 0u) {
        uint16_t length = (uint16_t)((uint32_t)audio_ble_atts_ccc_runtime_20073b00[0x14u] * 2u);
        *slot = (uint32_t)(uintptr_t)audio_wsf_buffer_alloc(length);
    }
    return *slot;
}
