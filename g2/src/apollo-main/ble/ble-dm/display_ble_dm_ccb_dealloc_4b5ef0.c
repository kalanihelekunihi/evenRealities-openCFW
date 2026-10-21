/* Cordio dmConnCcbDealloc 0x4b5ef0: FREE trace and CCB in-use clear. */
#include <stdint.h>

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
static const char free_tag[] = "FREE";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_conn.c";
static const char function[] = "dmConnCcbDealloc";
static const char message[] = "dmConnCcbDealloc %d";

void audio_ble_dm_ccb_dealloc_4b5ef0(void *ccb)
{
    uint8_t *c = (uint8_t *)ccb;
    uint8_t level;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
        audio_ble_hci_vendor_compare_44b610(free_tag, error_tag, 3u) == 0)
        level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(free_tag, warning_tag, 4u) == 0)
        level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u &&
             audio_ble_hci_vendor_compare_44b610(free_tag, info_tag, 4u) == 0)
        level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() != 0u)
        level = 4u;
    else {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_ble_hci_vendor_compare_44b610(module, hci_tag, 3u) != 0)
            audio_ble_hci_wsf_trace(free_tag, message, c[0x10u]);
        c[0x16u] = 0u;
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0xd4u,
                           message, c[0x10u]);
    c[0x16u] = 0u;
}
