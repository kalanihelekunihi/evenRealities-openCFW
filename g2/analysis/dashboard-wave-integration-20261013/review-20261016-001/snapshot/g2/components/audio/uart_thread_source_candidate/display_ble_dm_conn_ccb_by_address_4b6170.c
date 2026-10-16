/* Cordio dmConnCcbByBdAddr at stock Apollo Main 0x4b6170. The three-row
 * address search and miss INFO trace follow the pinned body and dm_conn.c. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];
extern uint32_t audio_ble_pair_address_equal_4d294a(const void *, const void *);
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
static const char function[] = "dmConnCcbByBdAddr";
static const char message[] = "dmConnIdByBdAddr not found";

void *audio_ble_dm_conn_ccb_by_address_4b6170(const void *address)
{
    for (uint32_t i = 0u; i < 3u; ++i) {
        uint8_t *c = audio_dm_connection_records + i * 0x30u;
        if (c[0x16u] != 0u &&
            audio_ble_pair_address_equal_4d294a(c, address) != 0u)
            return c;
    }
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
            audio_ble_hci_wsf_trace(info_tag, message);
        return 0;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x10au, message);
    return 0;
}
