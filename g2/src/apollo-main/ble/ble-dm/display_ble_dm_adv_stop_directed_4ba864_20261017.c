/* Cordio dmAdvStopDirected at stock Main 0x4ba864. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint8_t audio_ble_dm_leg_adv_type_20074fb3;
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_ble_hci_vendor_compare_44b610(
    const void *, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern void audio_ble_hci_wsf_trace(const char *, const char *, ...);
extern void HciLeSetAdvEnableCmd(uint8_t);

static const char error_tag[] = "ERR";
static const char warning_tag[] = "WARN";
static const char info_tag[] = "INFO";
static const char module[] = "DM";
static const char hci_tag[] = "HCI";
static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\dm\\dm_adv_leg.c";
static const char function[] = "dmAdvStopDirected";
static const char message[] = "dmAdvStopDirected: state: %d";

void audio_ble_dm_adv_stop_directed_4ba864(void)
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
        goto stop;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(level, module, source, function, 0x1d8u,
                           message, audio_ble_dm_adv_control[0x1du]);
stop:;
    const uint8_t state = audio_ble_dm_adv_control[0x1du];
    if (state == 1u || state == 2u || state == 3u) {
        audio_ble_dm_adv_control[0x1du] =
            audio_ble_dm_leg_adv_type_20074fb3 == 1u ? 4u : 5u;
        HciLeSetAdvEnableCmd(0u);
    }
}
