/* Cordio dmConnCmplStates at stock Apollo Main 0x4b5b24. Three CCB rows and
 * INFO trace follow the pinned body and registered Cordio dm_conn.c. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char function[] = "dmConnCmplStates";
static const char message[] = "dmConnCmplStates %d";

void *audio_ble_dm_conn_complete_states_4b5b24(void)
{
    for (uint32_t i = 0u; i < 3u; ++i) {
        uint8_t *c = audio_dm_connection_records + i * 0x30u;
        uint16_t handle = (uint16_t)c[0x0cu] | ((uint16_t)c[0x0du] << 8u);
        if (c[0x16u] == 0u ||
            (c[0x15u] != 2u && (c[0x15u] != 4u || handle != 0xffffu)))
            continue;
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
                audio_ble_hci_wsf_trace(info_tag, message, c[0x10u]);
            return c;
        }
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(level, module, source, function, 0x9bu,
                               message, c[0x10u]);
        return c;
    }
    return 0;
}
