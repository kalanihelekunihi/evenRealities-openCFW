#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern volatile uint8_t audio_ble_hci_controller_state_20071478[];
extern uint32_t audio_ble_link_mask_select_47ae78(uint32_t, uint8_t, uint8_t *);
extern const uint8_t *DmSecGetLocalIrk(void);
extern void DmPrivAddDevToResList(uint8_t, const uint8_t *, const uint8_t *,
                                  const uint8_t *, uint8_t, uint16_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_ble_wsf_trace(const char *, const char *, ...);

static const char warn[] = "WARN";
static const char error[] = "ERR";
static const char info[] = "INFO";
static const char app[] = "APP";
static const char hci[] = "HCI";
static const char message_text[] = "Invalid connId in AppAddDevToResList: %d";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_main.c";
static const char function[] = "AppAddDevToResList";

/* Native 0x4bb098. The record table uses 48-byte connection rows. */
void audio_ble_master_pair_event_4bb098(const void *message, uint8_t connection)
{
    if (connection == 0u) {
        uint8_t level = 0u;
        if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
            audio_ble_hci_vendor_compare_44b610(warn, error, 3u) == 0)
            level = 1u;
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
                 audio_ble_hci_vendor_compare_44b610(warn, warn, 4u) == 0)
            level = 2u;
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
                 audio_ble_hci_vendor_compare_44b610(warn, info, 4u) == 0)
            level = 3u;
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
            level = 4u;
        else if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                 audio_ble_hci_vendor_compare_44b610(app, hci, 3u) != 0)
            audio_ble_wsf_trace(warn, message_text, connection);
        if (level != 0u && (audio_log_flags() & 2u) != 0u)
            audio_log_extended(level, app, path, function, 400u,
                               message_text, connection);
        return;
    }
    const uint8_t *table = audio_ble_discovery_connection_records_200717b0;
    uint32_t record = *(const uint32_t *)(const void *)(table +
                        ((uint32_t)connection - 1u) * 0x30u);
    /* Native 0x20071509 is offset 0x91 within the 0x20071478 state block. */
    if (audio_ble_hci_controller_state_20071478[0x91u] == 0u)
        return;
    uint32_t link = audio_ble_link_mask_select_47ae78(record, 4u, 0);
    if (link == 0u)
        return;
    const uint8_t *selected = (const uint8_t *)(uintptr_t)link;
    const uint8_t *local_irk = DmSecGetLocalIrk();
    DmPrivAddDevToResList(selected[0x16u], selected + 0x10u, selected,
                          local_irk, 1u, *(const uint16_t *)message);
}
