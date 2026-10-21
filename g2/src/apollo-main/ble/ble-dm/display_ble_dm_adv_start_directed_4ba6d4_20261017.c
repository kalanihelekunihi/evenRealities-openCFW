/* Cordio dmAdvStartDirected at stock Main 0x4ba6d4. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);
extern void HciLeSetAdvEnableCmd(uint8_t);
extern void audio_ble_copy_address6_4d293c(void *, const void *);

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_adv_leg.c";
static const char function[] = "dmAdvStartDirected";
static const char message[] = "dmAdvStartDirected: state: %d";

void audio_ble_dm_adv_start_directed_4ba6d4(uint8_t adv_type,
                                               uint16_t duration,
                                               uint8_t addr_type,
                                               const uint8_t *peer_address)
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
            audio_ble_hci_wsf_trace(info_tag, message,
                                    audio_ble_dm_adv_control[0x1du]);
        goto start;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x1bdu,
                           message, audio_ble_dm_adv_control[0x1du]);
start:;
    if (audio_ble_dm_adv_control[0x1du] == 0u) {
        HciLeSetAdvEnableCmd(1u);
        audio_ble_dm_adv_control[0x1du] = adv_type == 1u ? 2u : 3u;
        audio_ble_dm_adv_control[0x20u] = (uint8_t)duration;
        audio_ble_dm_adv_control[0x21u] = (uint8_t)(duration >> 8);
        audio_ble_copy_address6_4d293c(audio_ble_dm_adv_control + 0x25u,
                                        peer_address);
        audio_ble_dm_adv_control[0x31u] = addr_type;
    }
}
